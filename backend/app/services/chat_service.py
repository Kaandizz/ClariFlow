import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from ..core.config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        self.similarity_threshold = 0.3  # Minimum relevance score to use document context
        self.max_history_length = 5  # Keep last 5 turns to save tokens
        
    async def chat(self, query: str, history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Handle universal chatbot queries - combining document-based and general chat.
        
        Args:
            query: User's query/message
            history: List of previous messages (optional)
            
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
            
            # Check if any documents exist
            available_documents = self.get_available_documents()
            
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
        """Handle general chat using OpenAI GPT with conversation history."""
        try:
            # Build conversation messages
            messages = [
                {
                    "role": "system", 
                    "content": """You are ClariFlow, a helpful and intelligent AI assistant. 
                    You can help with a wide range of topics including:
                    - General knowledge questions
                    - Problem solving and analysis
                    - Creative writing and brainstorming
                    - Technical explanations
                    - Educational topics
                    
                    Provide clear, accurate, and helpful responses. Be conversational but professional.
                    If you're continuing a conversation, maintain context from the chat history."""
                }
            ]
            
            # Add conversation history
            for i, message in enumerate(history):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message})
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "response": answer,
                "source": "openai",
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
        """Search through available documents for relevant information."""
        try:
            best_response = None
            best_score = 0
            
            for document_id in available_documents:
                try:
                    # Get collection for the document
                    collection = self.chroma_client.get_collection(name=document_id)
                    
                    # Search for relevant chunks
                    results = collection.query(
                        query_texts=[query],
                        n_results=3,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    if not results['documents'] or not results['documents'][0]:
                        continue
                    
                    # Calculate relevance score based on distance
                    distances = results['distances'][0] if results['distances'] else []
                    if distances:
                        # Convert distance to relevance score (lower distance = higher relevance)
                        avg_distance = sum(distances) / len(distances)
                        relevance_score = max(0, 1 - avg_distance)  # Normalize to 0-1
                        
                        if relevance_score > best_score:
                            # Prepare context from relevant chunks
                            context = "\n\n".join(results['documents'][0])
                            
                            # Build conversation messages with document context
                            messages = [
                                {
                                    "role": "system", 
                                    "content": f"""You are ClariFlow, an AI assistant that helps users understand their documents. 
                                    
                                    Context from the document:
                                    {context}
                                    
                                    Please answer the user's query based on the provided context. If the context doesn't contain enough information to answer the query completely, you can supplement with your general knowledge, but prioritize the document information. Be accurate and helpful."""
                                }
                            ]
                            
                            # Add conversation history
                            for i, message in enumerate(history):
                                role = "user" if i % 2 == 0 else "assistant"
                                messages.append({"role": role, "content": message})
                            
                            # Add current query
                            messages.append({"role": "user", "content": query})
                            
                            # Get response from OpenAI
                            response = self.client.chat.completions.create(
                                model="gpt-4",
                                messages=messages,
                                max_tokens=1000,
                                temperature=0.3
                            )
                            
                            answer = response.choices[0].message.content
                            
                            best_response = {
                                "answer": answer,
                                "sources": results['documents'][0],
                                "matched_chunks": results['documents'][0],
                                "document_id": document_id,
                                "relevance_score": relevance_score
                            }
                            best_score = relevance_score
                            
                except Exception as e:
                    logger.warning(f"Error searching document {document_id}: {str(e)}")
                    continue
            
            return best_response
            
        except Exception as e:
            logger.error(f"Error in document search: {str(e)}")
            return None
    
    def get_available_documents(self) -> List[str]:
        """Get list of available document IDs."""
        try:
            collections = self.chroma_client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error getting available documents: {str(e)}")
            return [] 