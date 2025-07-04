from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ToneType(str, Enum):
    FORMAL = "formal"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"

class EmailType(str, Enum):
    FOLLOW_UP = "follow_up"
    INTRODUCTION = "introduction"
    MEETING_REQUEST = "meeting_request"
    THANK_YOU = "thank_you"
    ANNOUNCEMENT = "announcement"
    CUSTOM = "custom"

class ProposalType(str, Enum):
    BUSINESS_PROPOSAL = "business_proposal"
    PROJECT_PROPOSAL = "project_proposal"
    PARTNERSHIP_PROPOSAL = "partnership_proposal"
    INVESTMENT_PROPOSAL = "investment_proposal"
    CUSTOM = "custom"

class EmailComposeRequest(BaseModel):
    """Request model for email composition"""
    subject: str = Field(..., description="Email subject line")
    recipient_name: Optional[str] = Field(default=None, description="Recipient's name")
    recipient_email: Optional[str] = Field(default=None, description="Recipient's email")
    sender_name: str = Field(..., description="Sender's name")
    sender_email: str = Field(..., description="Sender's email")
    email_type: EmailType = Field(..., description="Type of email to compose")
    tone: ToneType = Field(default=ToneType.PROFESSIONAL, description="Desired tone for the email")
    context: str = Field(..., description="Context and purpose of the email")
    key_points: Optional[List[str]] = Field(default=None, description="Key points to include")
    call_to_action: Optional[str] = Field(default=None, description="Desired call to action")
    word_limit: Optional[int] = Field(default=300, description="Approximate word limit for the email")
    include_signature: bool = Field(default=True, description="Whether to include email signature")

class EmailComposeResponse(BaseModel):
    """Response model for email composition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    body: str
    sender_name: str
    sender_email: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    email_type: EmailType
    tone: ToneType
    word_count: int
    generated_at: datetime = Field(default_factory=datetime.now)
    suggestions: Optional[List[str]] = Field(default=None, description="Suggestions for improvement")
    alternative_subjects: Optional[List[str]] = Field(default=None, description="Alternative subject lines")

class ProposalComposeRequest(BaseModel):
    """Request model for proposal composition"""
    title: str = Field(..., description="Proposal title")
    proposal_type: ProposalType = Field(..., description="Type of proposal")
    client_name: str = Field(..., description="Client or recipient name")
    company_name: str = Field(..., description="Your company name")
    project_description: str = Field(..., description="Description of the project or opportunity")
    objectives: List[str] = Field(..., description="Key objectives of the proposal")
    deliverables: List[str] = Field(..., description="Expected deliverables")
    timeline: Optional[str] = Field(default=None, description="Project timeline")
    budget_range: Optional[str] = Field(default=None, description="Budget range or estimate")
    tone: ToneType = Field(default=ToneType.PROFESSIONAL, description="Desired tone for the proposal")
    include_executive_summary: bool = Field(default=True, description="Whether to include executive summary")
    include_company_background: bool = Field(default=True, description="Whether to include company background")
    custom_sections: Optional[List[str]] = Field(default=None, description="Custom sections to include")

class ProposalComposeResponse(BaseModel):
    """Response model for proposal composition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: Dict[str, str] = Field(..., description="Proposal sections and content")
    proposal_type: ProposalType
    client_name: str
    company_name: str
    tone: ToneType
    word_count: int
    generated_at: datetime = Field(default_factory=datetime.now)
    sections_included: List[str] = Field(..., description="List of sections included in the proposal")
    suggestions: Optional[List[str]] = Field(default=None, description="Suggestions for improvement")

class CompositionHistory(BaseModel):
    """Model for tracking composition history"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    composition_type: str = Field(..., description="Type of composition (email/proposal)")
    title: str
    content_preview: str = Field(..., description="Preview of the generated content")
    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    usage_count: int = Field(default=0, description="Number of times this composition was used")

class CompositionListResponse(BaseModel):
    """Response model for composition history listing"""
    compositions: List[CompositionHistory]
    total_count: int
    page: int
    per_page: int 