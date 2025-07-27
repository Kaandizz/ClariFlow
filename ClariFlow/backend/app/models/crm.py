from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class CRMType(str, Enum):
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"
    PIPEDRIVE = "pipedrive"
    NOTION = "notion"
    AIRTABLE = "airtable"
    CUSTOM = "custom"

class WebhookEventType(str, Enum):
    LEAD_CREATED = "lead_created"
    LEAD_UPDATED = "lead_updated"
    LEAD_DELETED = "lead_deleted"
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    DEAL_CREATED = "deal_created"
    DEAL_UPDATED = "deal_updated"
    DEAL_STAGE_CHANGED = "deal_stage_changed"

class WebhookPayload(BaseModel):
    """Generic webhook payload structure"""
    event_type: WebhookEventType
    crm_type: CRMType
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(..., description="Event-specific data")
    source_id: Optional[str] = Field(default=None, description="Source record ID in the CRM")
    user_id: Optional[str] = Field(default=None, description="User who triggered the event")

class HubSpotWebhookPayload(BaseModel):
    """HubSpot specific webhook payload"""
    subscription_type: str
    portal_id: int
    object_type: str
    object_id: int
    change_source: str
    event_id: int
    app_id: Optional[int] = None
    occurred_at: int
    subscription_id: int
    attempt_number: int
    change_flag: str
    source_type: str
    property_name: Optional[str] = None
    property_value: Optional[str] = None
    source_id: Optional[str] = None
    source_label: Optional[str] = None

class CRMSyncRequest(BaseModel):
    """Request model for CRM sync operations"""
    crm_type: CRMType
    sync_type: str = Field(..., description="Type of sync operation")
    entity_type: Optional[str] = Field(default=None, description="Type of entity to sync")
    entity_ids: Optional[List[str]] = Field(default=None, description="Specific entity IDs to sync")
    sync_all: bool = Field(default=False, description="Whether to sync all entities")
    force_update: bool = Field(default=False, description="Whether to force update existing records")

class CRMSyncResponse(BaseModel):
    """Response model for CRM sync operations"""
    success: bool
    message: str
    synced_count: int = Field(default=0, description="Number of records synced")
    errors: Optional[List[str]] = Field(default=None, description="List of errors encountered")
    sync_timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional sync details")

class CRMConnection(BaseModel):
    """Model for CRM connection configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    crm_type: CRMType
    name: str = Field(..., description="Connection name")
    api_key: Optional[str] = Field(default=None, description="API key for the CRM")
    api_url: Optional[str] = Field(default=None, description="API base URL")
    webhook_url: Optional[str] = Field(default=None, description="Webhook URL for this connection")
    is_active: bool = Field(default=True, description="Whether the connection is active")
    last_sync: Optional[datetime] = Field(default=None, description="Last successful sync timestamp")
    sync_frequency: Optional[str] = Field(default=None, description="Sync frequency (e.g., 'daily', 'hourly')")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CRMConnectionCreate(BaseModel):
    """Request model for creating CRM connection"""
    crm_type: CRMType
    name: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    webhook_url: Optional[str] = None
    sync_frequency: Optional[str] = None

class CRMConnectionUpdate(BaseModel):
    """Request model for updating CRM connection"""
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: Optional[bool] = None
    sync_frequency: Optional[str] = None

class CRMConnectionList(BaseModel):
    """Response model for CRM connection listing"""
    connections: List[CRMConnection]
    total_count: int

class WebhookVerificationRequest(BaseModel):
    """Request model for webhook verification"""
    crm_type: CRMType
    challenge: Optional[str] = Field(default=None, description="Verification challenge from CRM")
    verification_token: Optional[str] = Field(default=None, description="Verification token")

class WebhookVerificationResponse(BaseModel):
    """Response model for webhook verification"""
    success: bool
    message: str
    challenge_response: Optional[str] = Field(default=None, description="Response to verification challenge") 