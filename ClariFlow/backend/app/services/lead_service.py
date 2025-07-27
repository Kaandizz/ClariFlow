from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.lead import Lead, LeadCreate, LeadUpdate, LeadStatus
from ..utils.logger import setup_logger
import httpx

logger = setup_logger(__name__)

class LeadService:
    def __init__(self):
        self.notion_api_key = None
        self.notion_database_id = None
        self.airtable_api_key = None
        self.airtable_base_id = None
        self.airtable_table_name = None
        
        # Load CRM configuration from environment
        self._load_crm_config()
    
    def _load_crm_config(self):
        """Load CRM API keys and configuration from environment variables."""
        import os
        self.notion_api_key = os.getenv("NOTION_API_KEY")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        self.airtable_api_key = os.getenv("AIRTABLE_API_KEY")
        self.airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
        self.airtable_table_name = os.getenv("AIRTABLE_TABLE_NAME", "Leads")
    
    def create_lead(self, db: Session, lead_data: LeadCreate) -> Lead:
        """Create a new lead."""
        try:
            # Check if email already exists
            existing_lead = db.query(Lead).filter(Lead.email == lead_data.email.lower()).first()
            if existing_lead:
                raise ValueError(f"Lead with email {lead_data.email} already exists")
            
            # Create new lead
            lead = Lead(
                name=lead_data.name,
                email=lead_data.email.lower(),
                phone=lead_data.phone,
                source=lead_data.source,
                status=lead_data.status,
                notes=lead_data.notes
            )
            
            db.add(lead)
            db.commit()
            db.refresh(lead)
            
            logger.info(f"Created new lead: {lead.id} - {lead.name} ({lead.email})")
            return lead
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating lead: {str(e)}")
            raise
    
    def get_lead(self, db: Session, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            return lead
        except Exception as e:
            logger.error(f"Error getting lead {lead_id}: {str(e)}")
            raise
    
    def get_leads(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[LeadStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[Lead], int]:
        """Get leads with pagination and filtering."""
        try:
            query = db.query(Lead)
            
            # Apply status filter
            if status:
                query = query.filter(Lead.status == status)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Lead.name.ilike(search_term),
                        Lead.email.ilike(search_term),
                        Lead.phone.ilike(search_term),
                        Lead.source.ilike(search_term),
                        Lead.notes.ilike(search_term)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            leads = query.order_by(desc(Lead.created_at)).offset(skip).limit(limit).all()
            
            return leads, total
            
        except Exception as e:
            logger.error(f"Error getting leads: {str(e)}")
            raise
    
    def update_lead(self, db: Session, lead_id: str, lead_data: LeadUpdate) -> Optional[Lead]:
        """Update a lead."""
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return None
            
            # Check if email is being updated and if it already exists
            if lead_data.email and lead_data.email != lead.email:
                existing_lead = db.query(Lead).filter(
                    and_(Lead.email == lead_data.email.lower(), Lead.id != lead_id)
                ).first()
                if existing_lead:
                    raise ValueError(f"Lead with email {lead_data.email} already exists")
            
            # Update fields
            update_data = lead_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'email' and value:
                    setattr(lead, field, value.lower())
                else:
                    setattr(lead, field, value)
            
            lead.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(lead)
            
            logger.info(f"Updated lead: {lead.id} - {lead.name}")
            return lead
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating lead {lead_id}: {str(e)}")
            raise
    
    def delete_lead(self, db: Session, lead_id: str) -> bool:
        """Delete a lead."""
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return False
            
            db.delete(lead)
            db.commit()
            
            logger.info(f"Deleted lead: {lead_id} - {lead.name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting lead {lead_id}: {str(e)}")
            raise
    
    def set_reminder(self, db: Session, lead_id: str, reminder_time: datetime) -> Optional[Lead]:
        """Set a reminder time for a lead."""
        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return None
            
            lead.reminder_time = reminder_time
            lead.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(lead)
            
            logger.info(f"Set reminder for lead {lead_id} at {reminder_time}")
            return lead
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting reminder for lead {lead_id}: {str(e)}")
            raise
    
    def get_upcoming_reminders(self, db: Session, hours_ahead: int = 24) -> List[Lead]:
        """Get leads with reminders in the next N hours."""
        try:
            now = datetime.utcnow()
            future_time = now + timedelta(hours=hours_ahead)
            
            leads = db.query(Lead).filter(
                and_(
                    Lead.reminder_time.isnot(None),
                    Lead.reminder_time >= now,
                    Lead.reminder_time <= future_time
                )
            ).order_by(Lead.reminder_time).all()
            
            return leads
            
        except Exception as e:
            logger.error(f"Error getting upcoming reminders: {str(e)}")
            raise
    
    async def sync_to_notion(self, leads: List[Lead]) -> Dict[str, Any]:
        """Sync leads to Notion database."""
        if not self.notion_api_key or not self.notion_database_id:
            return {
                "success": False,
                "message": "Notion API key or database ID not configured",
                "synced_leads": 0,
                "errors": ["Missing Notion configuration"]
            }
        
        synced_count = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.notion_api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            
            for lead in leads:
                try:
                    # Create page in Notion database
                    page_data = {
                        "parent": {"database_id": self.notion_database_id},
                        "properties": {
                            "Name": {"title": [{"text": {"content": lead.name}}]},
                            "Email": {"email": lead.email},
                            "Status": {"select": {"name": lead.status.value}},
                            "Source": {"rich_text": [{"text": {"content": lead.source or ""}}]},
                            "Phone": {"phone_number": lead.phone or ""},
                            "Notes": {"rich_text": [{"text": {"content": lead.notes or ""}}]},
                            "Created": {"date": {"start": lead.created_at.isoformat()}}
                        }
                    }
                    
                    response = await client.post(
                        "https://api.notion.com/v1/pages",
                        headers=headers,
                        json=page_data
                    )
                    
                    if response.status_code == 200:
                        synced_count += 1
                        logger.info(f"Synced lead {lead.id} to Notion")
                    else:
                        errors.append(f"Failed to sync lead {lead.id}: {response.text}")
                        
                except Exception as e:
                    errors.append(f"Error syncing lead {lead.id}: {str(e)}")
        
        return {
            "success": synced_count > 0,
            "message": f"Synced {synced_count} leads to Notion",
            "synced_leads": synced_count,
            "errors": errors if errors else None
        }
    
    async def sync_to_airtable(self, leads: List[Lead]) -> Dict[str, Any]:
        """Sync leads to Airtable."""
        if not self.airtable_api_key or not self.airtable_base_id:
            return {
                "success": False,
                "message": "Airtable API key or base ID not configured",
                "synced_leads": 0,
                "errors": ["Missing Airtable configuration"]
            }
        
        synced_count = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.airtable_api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare records for batch creation
            records = []
            for lead in leads:
                record = {
                    "fields": {
                        "Name": lead.name,
                        "Email": lead.email,
                        "Status": lead.status.value,
                        "Source": lead.source or "",
                        "Phone": lead.phone or "",
                        "Notes": lead.notes or "",
                        "Created": lead.created_at.isoformat()
                    }
                }
                records.append(record)
            
            try:
                # Create records in batches of 10 (Airtable limit)
                batch_size = 10
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    response = await client.post(
                        f"https://api.airtable.com/v0/{self.airtable_base_id}/{self.airtable_table_name}",
                        headers=headers,
                        json={"records": batch}
                    )
                    
                    if response.status_code == 200:
                        synced_count += len(batch)
                        logger.info(f"Synced batch of {len(batch)} leads to Airtable")
                    else:
                        errors.append(f"Failed to sync batch: {response.text}")
                        
            except Exception as e:
                errors.append(f"Error syncing to Airtable: {str(e)}")
        
        return {
            "success": synced_count > 0,
            "message": f"Synced {synced_count} leads to Airtable",
            "synced_leads": synced_count,
            "errors": errors if errors else None
        }
    
    async def sync_to_crm(self, db: Session, crm_type: str, lead_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Sync leads to external CRM system."""
        try:
            # Get leads to sync
            if lead_ids:
                leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
            else:
                leads = db.query(Lead).all()
            
            if not leads:
                return {
                    "success": False,
                    "message": "No leads found to sync",
                    "synced_leads": 0,
                    "errors": ["No leads available"]
                }
            
            # Sync based on CRM type
            if crm_type.lower() == "notion":
                result = await self.sync_to_notion(leads)
            elif crm_type.lower() == "airtable":
                result = await self.sync_to_airtable(leads)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported CRM type: {crm_type}",
                    "synced_leads": 0,
                    "errors": [f"CRM type '{crm_type}' not supported"]
                }
            
            logger.info(f"CRM sync completed: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in CRM sync: {str(e)}")
            return {
                "success": False,
                "message": f"Error during CRM sync: {str(e)}",
                "synced_leads": 0,
                "errors": [str(e)]
            } 