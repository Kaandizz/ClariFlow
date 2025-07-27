import os
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
from .embedding import EmbeddingService
from ..models.search import SearchResult
from ..core.config import settings

class SearchService:
    def __init__(self):
        """Initialize the search service."""
        self.embedding_service = EmbeddingService()
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )

    def search_documents(self, query: str, file_id: Optional[str] = None, top_k: int = 5) -> List[SearchResult]:
        """
        Perform semantic search across document chunks.
        
        Args:
            query: The search query text
            file_id: Optional document ID to search within a specific document
            top_k: Number of top results to return
            
        Returns:
            List of SearchResult objects with relevant chunks
        """
        try:
            # Create embedding for the query
            query_embedding = self.embedding_service.create_embeddings([query])[0]
            
            results = []
            
            if file_id:
                # Search within a specific document collection
                try:
                    collection = self.chroma_client.get_collection(name=file_id)
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=top_k,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    if search_results['documents'] and search_results['documents'][0]:
                        results.extend(self._process_search_results(
                            search_results, query, top_k
                        ))
                        
                except Exception as e:
                    # Document collection not found, return empty results
                    print(f"Document collection {file_id} not found: {e}")
                    return []
            else:
                # Search across all document collections
                collections = self.chroma_client.list_collections()
                
                for collection_info in collections:
                    try:
                        collection = self.chroma_client.get_collection(name=collection_info.name)
                        search_results = collection.query(
                            query_embeddings=[query_embedding],
                            n_results=top_k,
                            include=["documents", "metadatas", "distances"]
                        )
                        
                        if search_results['documents'] and search_results['documents'][0]:
                            results.extend(self._process_search_results(
                                search_results, query, top_k
                            ))
                            
                    except Exception as e:
                        print(f"Error searching collection {collection_info.name}: {e}")
                        continue
            
            # Sort by score and return top_k results
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            raise Exception(f"Error performing search: {str(e)}")

    def _process_search_results(self, search_results: Dict[str, Any], query: str, top_k: int) -> List[SearchResult]:
        """
        Process raw search results into SearchResult objects.
        
        Args:
            search_results: Raw results from ChromaDB
            query: Original search query
            top_k: Number of results to return
            
        Returns:
            List of processed SearchResult objects
        """
        results = []
        
        if not search_results['documents'] or not search_results['documents'][0]:
            return results
            
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # Convert distance to similarity score (ChromaDB returns L2 distance)
            # Higher distance = lower similarity, so we convert to a 0-1 scale
            score = max(0, 1 - distance)
            
            # Extract source file name from metadata
            source_file = metadata.get('source', 'Unknown')
            if isinstance(source_file, str):
                source_file = os.path.basename(source_file)
            
            # Extract page number if available
            page_number = None
            if 'page' in metadata:
                page_number = metadata['page']
            
            # Extract chunk index
            chunk_index = metadata.get('chunk_index')
            
            results.append(SearchResult(
                text=doc,
                score=round(score, 3),
                source_file=source_file,
                page_number=page_number,
                chunk_index=chunk_index
            ))
        
        return results

    def get_available_documents(self) -> List[Dict[str, str]]:
        """
        Get list of available documents for search.
        
        Returns:
            List of document information dictionaries
        """
        try:
            collections = self.chroma_client.list_collections()
            documents = []
            
            for collection_info in collections:
                try:
                    collection = self.chroma_client.get_collection(name=collection_info.name)
                    # Get a sample document to extract metadata
                    sample = collection.get(limit=1)
                    
                    if sample['metadatas'] and sample['metadatas'][0]:
                        metadata = sample['metadatas'][0]
                        source_file = metadata.get('source', 'Unknown')
                        if isinstance(source_file, str):
                            source_file = os.path.basename(source_file)
                        
                        documents.append({
                            'document_id': collection_info.name,
                            'source_file': source_file,
                            'chunk_count': collection.count()
                        })
                except Exception as e:
                    print(f"Error getting info for collection {collection_info.name}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error getting available documents: {str(e)}") 