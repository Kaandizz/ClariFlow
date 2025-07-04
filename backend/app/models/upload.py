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
    status: UploadStatus
    error_message: Optional[str] = None
    chunk_count: Optional[int] = None
    document_id: Optional[str] = None

class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    message: str
    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: List[FileUploadResult]

class DocumentChunk(BaseModel):
    """Model for document chunks"""
    content: str
    metadata: dict 