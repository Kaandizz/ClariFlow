from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    query: str
    file_id: Optional[str] = None
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    """Model for individual search results."""
    text: str
    score: float
    source_file: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None

class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    results: List[SearchResult]
    total_results: int
    query: str 