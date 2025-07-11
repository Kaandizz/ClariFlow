from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListResponse, 
    LeadReminderRequest, CRMSyncRequest, CRMSyncResponse, LeadStatus
)
from ..models.user import User
from ..services.lead_service import LeadService
from ..services.reminder_scheduler import reminder_scheduler
from ..core.database import get_db
from ..core.security import get_current_active_user
from ..utils.logger import setup_logger

router = APIRouter()
lead_service = LeadService()
logger = setup_logger(__name__)

@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new lead.
    
    Args:
        lead_data: Lead creation data
        db: Database session
        
    Returns:
        Created lead information
    """
    try:
        logger.info(f"Creating new lead: {lead_data.name} ({lead_data.email})")
        
        lead = lead_service.create_lead(db, lead_data)
        
        # Convert to response model
        response = LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            status=lead.status,
            notes=lead.notes,
            reminder_time=lead.reminder_time,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
        
        logger.info(f"Successfully created lead: {lead.id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error creating lead: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leads", response_model=LeadListResponse)
async def get_leads(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[LeadStatus] = Query(None, description="Filter by lead status"),
    search: Optional[str] = Query(None, description="Search in name, email, phone, source, notes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all leads with pagination and filtering.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Number of records to return
        status: Filter by lead status
        search: Search term for filtering
        db: Database session
        
    Returns:
        Paginated list of leads
    """
    try:
        logger.info(f"Getting leads: skip={skip}, limit={limit}, status={status}, search={search}")
        
        leads, total = lead_service.get_leads(db, skip=skip, limit=limit, status=status, search=search)
        
        # Convert to response models
        lead_responses = []
        for lead in leads:
            response = LeadResponse(
                id=lead.id,
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                source=lead.source,
                status=lead.status,
                notes=lead.notes,
                reminder_time=lead.reminder_time,
                created_at=lead.created_at,
                updated_at=lead.updated_at
            )
            lead_responses.append(response)
        
        result = LeadListResponse(
            leads=lead_responses,
            total=total,
            page=(skip // limit) + 1,
            per_page=limit
        )
        
        logger.info(f"Retrieved {len(leads)} leads out of {total} total")
        return result
        
    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, db: Session = Depends(get_db)):
    """
    Get a specific lead by ID.
    
    Args:
        lead_id: The ID of the lead
        db: Database session
        
    Returns:
        Lead information
    """
    try:
        logger.info(f"Getting lead: {lead_id}")
        
        lead = lead_service.get_lead(db, lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        response = LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            status=lead.status,
            notes=lead.notes,
            reminder_time=lead.reminder_time,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    """
    Update a lead.
    
    Args:
        lead_id: The ID of the lead
        lead_data: Updated lead data
        db: Database session
        
    Returns:
        Updated lead information
    """
    try:
        logger.info(f"Updating lead: {lead_id}")
        
        lead = lead_service.update_lead(db, lead_id, lead_data)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        response = LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            status=lead.status,
            notes=lead.notes,
            reminder_time=lead.reminder_time,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
        
        logger.info(f"Successfully updated lead: {lead_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error updating lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, db: Session = Depends(get_db)):
    """
    Delete a lead.
    
    Args:
        lead_id: The ID of the lead
        db: Database session
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Deleting lead: {lead_id}")
        
        success = lead_service.delete_lead(db, lead_id)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.info(f"Successfully deleted lead: {lead_id}")
        return {"message": "Lead deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/leads/{lead_id}/reminder", response_model=LeadResponse)
async def set_lead_reminder(lead_id: str, reminder_data: LeadReminderRequest, db: Session = Depends(get_db)):
    """
    Set a reminder time for a lead.
    
    Args:
        lead_id: The ID of the lead
        reminder_data: Reminder time data
        db: Database session
        
    Returns:
        Updated lead information
    """
    try:
        logger.info(f"Setting reminder for lead {lead_id} at {reminder_data.reminder_time}")
        
        lead = lead_service.set_reminder(db, lead_id, reminder_data.reminder_time)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        response = LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            status=lead.status,
            notes=lead.notes,
            reminder_time=lead.reminder_time,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
        
        logger.info(f"Successfully set reminder for lead: {lead_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting reminder for lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leads/reminders/upcoming")
async def get_upcoming_reminders(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours ahead to check for reminders"),
    db: Session = Depends(get_db)
):
    """
    Get leads with upcoming reminders.
    
    Args:
        hours_ahead: Number of hours ahead to check for reminders
        db: Database session
        
    Returns:
        List of leads with upcoming reminders
    """
    try:
        logger.info(f"Getting upcoming reminders for next {hours_ahead} hours")
        
        leads = lead_service.get_upcoming_reminders(db, hours_ahead=hours_ahead)
        
        # Convert to response models
        lead_responses = []
        for lead in leads:
            response = LeadResponse(
                id=lead.id,
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                source=lead.source,
                status=lead.status,
                notes=lead.notes,
                reminder_time=lead.reminder_time,
                created_at=lead.created_at,
                updated_at=lead.updated_at
            )
            lead_responses.append(response)
        
        logger.info(f"Found {len(leads)} leads with upcoming reminders")
        return {"leads": lead_responses, "count": len(leads)}
        
    except Exception as e:
        logger.error(f"Error getting upcoming reminders: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/crm/sync", response_model=CRMSyncResponse)
async def sync_to_crm(
    sync_request: CRMSyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Sync leads to external CRM system.
    
    Args:
        sync_request: CRM sync configuration
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Sync operation result
    """
    try:
        logger.info(f"Starting CRM sync: type={sync_request.crm_type}, sync_all={sync_request.sync_all}")
        
        # Add sync task to background tasks
        background_tasks.add_task(
            lead_service.sync_to_crm,
            db,
            sync_request.crm_type,
            sync_request.lead_ids if not sync_request.sync_all else None
        )
        
        # Return immediate response
        message = f"CRM sync started for {sync_request.crm_type}"
        if sync_request.sync_all:
            message += " (all leads)"
        elif sync_request.lead_ids:
            message += f" ({len(sync_request.lead_ids)} specific leads)"
        
        return CRMSyncResponse(
            success=True,
            message=message,
            synced_leads=0,  # Will be updated in background
            errors=None
        )
        
    except Exception as e:
        logger.error(f"Error starting CRM sync: {str(e)}")
        return CRMSyncResponse(
            success=False,
            message=f"Error starting CRM sync: {str(e)}",
            synced_leads=0,
            errors=[str(e)]
        )

@router.get("/crm/status")
async def get_crm_status():
    """
    Get CRM integration status and configuration.
    
    Returns:
        CRM configuration status
    """
    try:
        status = {
            "notion": {
                "configured": bool(lead_service.notion_api_key and lead_service.notion_database_id),
                "api_key_set": bool(lead_service.notion_api_key),
                "database_id_set": bool(lead_service.notion_database_id)
            },
            "airtable": {
                "configured": bool(lead_service.airtable_api_key and lead_service.airtable_base_id),
                "api_key_set": bool(lead_service.airtable_api_key),
                "base_id_set": bool(lead_service.airtable_base_id),
                "table_name": lead_service.airtable_table_name
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting CRM status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get reminder scheduler status and configuration.
    
    Returns:
        Scheduler status information
    """
    try:
        status = reminder_scheduler.get_scheduler_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 