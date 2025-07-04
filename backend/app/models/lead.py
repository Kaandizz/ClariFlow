from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid
import enum

# Enum for lead status
class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    FOLLOW_UP = "follow-up"
    CONVERTED = "converted"

# SQLAlchemy Database Model
class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)  # e.g., "website", "referral", "cold_call"
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    reminder_time = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Models for API
class LeadBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    source: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower() if v else v

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v

class LeadResponse(LeadBase):
    id: str
    reminder_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadReminderRequest(BaseModel):
    reminder_time: datetime

class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    per_page: int

class CRMSyncRequest(BaseModel):
    crm_type: str  # "notion", "airtable", "hubspot"
    sync_all: bool = False
    lead_ids: Optional[List[str]] = None

class CRMSyncResponse(BaseModel):
    success: bool
    message: str
    synced_leads: int
    errors: Optional[List[str]] = None 