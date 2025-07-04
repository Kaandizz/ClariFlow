from fastapi import APIRouter, HTTPException
from ..services.search_service import SearchService
from ..models.search import SearchRequest, SearchResponse
from ..utils.logger import setup_logger

router = APIRouter()
search_service = SearchService()
logger = setup_logger(__name__)

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Perform semantic search across uploaded documents.
    
    Args:
        request: SearchRequest containing query and optional filters
        
    Returns:
        SearchResponse with relevant document chunks
        
    Raises:
        HTTPException: If search fails or no documents are available
    """
    try:
        logger.info(f"Performing search for query: '{request.query}'")
        
        # Validate query
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # Perform search
        results = search_service.search_documents(
            query=request.query,
            file_id=request.file_id,
            top_k=request.top_k
        )
        
        logger.info(f"Search completed. Found {len(results)} results")
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )

@router.get("/documents")
async def get_available_documents():
    """
    Get list of available documents for search.
    
    Returns:
        List of document information
    """
    try:
        documents = search_service.get_available_documents()
        return {
            "documents": documents,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error getting available documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        ) 