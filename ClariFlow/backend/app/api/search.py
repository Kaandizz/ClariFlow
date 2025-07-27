from fastapi import APIRouter, HTTPException, Depends
from ..services.search_service import SearchService
from ..models.search import SearchRequest, SearchResponse
from ..core.security import get_current_active_user
from ..models.user import User
from ..utils.logger import setup_logger

router = APIRouter()
search_service = SearchService()
logger = setup_logger(__name__)

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform semantic search across uploaded documents.
    
    Args:
        request: SearchRequest containing query and optional filters
        current_user: Current authenticated user
        
    Returns:
        SearchResponse with relevant document chunks
        
    Raises:
        HTTPException: If search fails or no documents are available
    """
    try:
        logger.info(f"Performing search for user {current_user.email}: '{request.query}'")
        
        # Validate query
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # Perform search with user context
        results = search_service.search_documents(
            query=request.query,
            file_id=request.file_id,
            top_k=request.top_k or 5  # Default to 5 if None
        )
        
        logger.info(f"Search completed for user {current_user.email}. Found {len(results)} results")
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Search error for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )

@router.get("/documents")
async def get_available_documents(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of available documents for search.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of document information for the current user
    """
    try:
        logger.info(f"Getting available documents for user {current_user.email}")
        
        documents = search_service.get_available_documents()
        
        logger.info(f"Retrieved {len(documents)} documents for user {current_user.email}")
        
        return {
            "documents": documents,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error getting available documents for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        ) 