from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class UploadStatus(str, Enum):
    """Status of file upload processing."""
    SUCCESS = "success"
    ERROR = "error"

class FileUploadResult(BaseModel):
    """Result for a single file upload."""
    filename: str
    status: str  # Allow both enum and string for flexibility
    error_message: Optional[str] = None
    chunks_processed: Optional[int] = None
    document_id: Optional[str] = None

class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    results: List[FileUploadResult]
    total_files: int
    successful_count: int
    failed_count: int

class DocumentChunk(BaseModel):
    """Model for document chunks"""
    content: str
    metadata: dict 