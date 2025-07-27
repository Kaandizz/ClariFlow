from typing import Optional, List, Dict, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from ..core.config import settings
from ..utils.logger import setup_logger
from .ai_client import ai_client
from ..utils.model_router import FeatureType

logger = setup_logger(__name__)

class ChatService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD  # Minimum relevance score to use document context
        self.max_history_length = settings.MAX_HISTORY_LENGTH  # Keep last N turns to save tokens
        
    async def chat(self, query: str, history: Optional[List[str]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle universal chatbot queries - combining document-based and general chat.
        
        Args:
            query: User's query/message
            history: List of previous messages (optional)
            user_id: Optional user ID for document filtering
            
        Returns:
            Dictionary with response, source, and optional metadata
        """
        try:
            logger.info(f"Processing universal chat query: '{query[:50]}...'")
            
            # Normalize history
            if history is None:
                history = []
            
            # Truncate history to save tokens
            history = history[-self.max_history_length:]
            
            # Check if any documents exist for this user
            available_documents = self.get_available_documents(user_id)
            
            if not available_documents:
                # No documents available, use general OpenAI chat
                logger.info("No documents available, using general OpenAI chat")
                return await self._handle_general_chat(query, history)
            
            # Documents exist, try to find relevant information
            document_response = await self._try_document_search(query, available_documents, history)
            
            if document_response and document_response.get("relevance_score", 0) > self.similarity_threshold:
                # Document found relevant information
                logger.info(f"Using document-based response with relevance score: {document_response['relevance_score']}")
                return {
                    "response": document_response["answer"],
                    "source": "document",
                    "sources": document_response["sources"],
                    "document_id": document_response["document_id"],
                    "timestamp": datetime.now(),
                    "used_context": True,
                    "matched_chunks": document_response["matched_chunks"],
                    "relevance_score": document_response["relevance_score"]
                }
            else:
                # No relevant document information found, use general chat
                logger.info("No relevant document information found, using general OpenAI chat")
                return await self._handle_general_chat(query, history)
                
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "source": "openai",
                "sources": None,
                "document_id": None,
                "timestamp": datetime.now(),
                "used_context": False,
                "matched_chunks": None,
                "relevance_score": None
            }
    
    async def _handle_general_chat(self, query: str, history: List[str]) -> Dict[str, Any]:
        """Handle general chat using AI client with conversation history."""
        try:
            # Use AI client for chat response
            response = await ai_client.chat_response(query, history)
            
            return {
                "response": response["content"],
                "source": response["model_used"],
                "sources": None,
                "document_id": None,
                "timestamp": datetime.now(),
                "used_context": False,
                "matched_chunks": None,
                "relevance_score": None
            }
            
        except Exception as e:
            logger.error(f"Error in general chat handling: {str(e)}")
            raise
    
    async def _try_document_search(self, query: str, available_documents: List[str], history: List[str]) -> Optional[Dict[str, Any]]:
        """Search through available documents for relevant information with improved error handling."""
        try:
            best_response = None
            best_score = 0
            search_errors = []
            
            for document_id in available_documents:
                try:
                    # Get collection for the document
                    collection = self.chroma_client.get_collection(name=document_id)
                    
                    # Validate collection has content
                    if collection.count() == 0:
                        logger.warning(f"Collection {document_id} is empty, skipping")
                        continue
                    
                    # Search for relevant chunks with more results for better context
                    results = collection.query(
                        query_texts=[query],
                        n_results=5,  # Increased from 3 for better context
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    if not results['documents'] or not results['documents'][0]:
                        continue
                    
                    # Calculate relevance score based on distance with improved scoring
                    distances = results['distances'][0] if results['distances'] else []
                    if distances:
                        # Improved relevance scoring: consider both average and best distance
                        avg_distance = sum(distances) / len(distances)
                        min_distance = min(distances)
                        
                        # Weighted score: 70% best match, 30% average
                        relevance_score = max(0, 1 - (0.7 * min_distance + 0.3 * avg_distance))
                        
                        # Only consider if score is above threshold
                        if relevance_score > self.similarity_threshold and relevance_score > best_score:
                            # Prepare context from relevant chunks with better formatting
                            context_chunks = results['documents'][0]
                            context = "\n\n---\n\n".join(context_chunks)
                            
                            # Build conversation messages with improved document context
                            messages = [
                                {
                                    "role": "system", 
                                    "content": f"""You are ClariFlow, an AI assistant that helps users understand their documents. 
                                    
                                    Context from the document:
                                    {context}
                                    
                                    Please answer the user's query based on the provided context. If the context doesn't contain enough information to answer the query completely, you can supplement with your general knowledge, but prioritize the document information. Be accurate and helpful.
                                    
                                    If the context is not relevant to the query, say so clearly."""
                                }
                            ]
                            
                            # Add conversation history
                            for i, message in enumerate(history):
                                role = "user" if i % 2 == 0 else "assistant"
                                messages.append({"role": role, "content": message})
                            
                            # Add current query
                            messages.append({"role": "user", "content": query})
                            
                            # Get response from AI client with better parameters
                            response = await ai_client.generate_response(
                                messages=messages,
                                feature_type=FeatureType.SEARCH,
                                max_tokens=1200,  # Increased for better responses
                                temperature=0.3
                            )
                            
                            answer = response["content"]
                            
                            best_response = {
                                "answer": answer,
                                "sources": results['documents'][0],
                                "matched_chunks": results['documents'][0],
                                "document_id": document_id,
                                "relevance_score": relevance_score
                            }
                            best_score = relevance_score
                            
                except Exception as e:
                    error_msg = f"Error searching document {document_id}: {str(e)}"
                    search_errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
            
            # Log search summary
            if search_errors:
                logger.warning(f"Search completed with {len(search_errors)} errors: {search_errors[:3]}...")
            else:
                logger.info("Document search completed successfully")
            
            return best_response
            
        except Exception as e:
            logger.error(f"Error in document search: {str(e)}")
            return None
    
    def get_available_documents(self, user_id: Optional[str] = None) -> List[str]:
        """
        Get list of available document IDs with validation.
        
        Args:
            user_id: Optional user ID to filter documents by user
            
        Returns:
            List of valid document IDs
        """
        try:
            collections = self.chroma_client.list_collections()
            valid_documents = []
            
            for collection in collections:
                try:
                    # Validate collection has content
                    collection_obj = self.chroma_client.get_collection(name=collection.name)
                    count = collection_obj.count()
                    
                    if count > 0:
                        # Check if this document belongs to the user (if user_id provided)
                        if user_id:
                            # Get sample metadata to check user ownership
                            sample = collection_obj.get(limit=1)
                            if sample['metadatas'] and sample['metadatas'][0]:
                                metadata = sample['metadatas'][0]
                                doc_user_id = metadata.get('user_id')
                                if doc_user_id == user_id:
                                    valid_documents.append(collection.name)
                        else:
                            # No user filtering, include all valid documents
                            valid_documents.append(collection.name)
                            
                except Exception as e:
                    logger.warning(f"Invalid collection {collection.name}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(valid_documents)} valid documents")
            return valid_documents
            
        except Exception as e:
            logger.error(f"Error getting available documents: {str(e)}")
            return [] 