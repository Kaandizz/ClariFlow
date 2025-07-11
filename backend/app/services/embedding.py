import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from ..core.config import settings

class EmbeddingService:
    def __init__(self):
        """Initialize the embedding service with OpenAI embeddings."""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings to create embeddings for
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)

    def store_embeddings(self, texts: List[str], metadatas: List[dict] = None, collection_name: Optional[str] = None):
        """
        Store text embeddings in ChromaDB.
        
        Args:
            texts: List of text strings to store
            metadatas: Optional list of metadata dictionaries for each text
            collection_name: Optional collection name (uses default if not provided)
        """
        # Create or get collection
        if collection_name:
            try:
                collection = self.chroma_client.get_collection(name=collection_name)
            except:
                collection = self.chroma_client.create_collection(name=collection_name)
        else:
            collection = self.chroma_client.get_or_create_collection(name="default")
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Prepare IDs
        ids = [f"chunk_{i}" for i in range(len(texts))]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas or [{}] * len(texts),
            ids=ids
        )

    def get_embeddings(self):
        return self.embeddings 