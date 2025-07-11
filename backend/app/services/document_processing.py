import os
import uuid
import hashlib
from typing import List, Optional, Tuple, Dict
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from .embedding import EmbeddingService
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_service = EmbeddingService()

    def validate_file(self, file_path: str, file_size: int, max_size: int = 10 * 1024 * 1024) -> Tuple[bool, Optional[str]]:
        """
        Validate a file for processing.
        
        Args:
            file_path: Path to the file
            file_size: Size of the file in bytes
            max_size: Maximum allowed file size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file_size > max_size:
            return False, f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum allowed size ({max_size / (1024*1024)}MB)"
        
        # Check file extension
        allowed_extensions = {'.pdf', '.docx', '.txt', '.csv', '.xlsx', '.xls', '.md'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in allowed_extensions:
            return False, f"Unsupported file type '{file_ext}'. Allowed types: {', '.join(allowed_extensions)}"
        
        return True, None

    def get_file_hash(self, file_path: str) -> str:
        """
        Generate SHA-256 hash of a file for duplicate detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash string
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document based on its file extension.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
            
        Raises:
            ValueError: If file type is not supported
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_ext == '.docx':
                loader = Docx2txtLoader(file_path)
            elif file_ext == '.txt':
                loader = TextLoader(file_path)
            elif file_ext == '.csv':
                loader = CSVLoader(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                loader = UnstructuredExcelLoader(file_path)
            elif file_ext == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return loader.load()
        except Exception as e:
            raise Exception(f"Error loading document: {str(e)}")

    def process_file(self, file_path: str, user_id: Optional[str] = None) -> Tuple[str, int]:
        """
        Process a single file: load, split, and store embeddings.
        
        Args:
            file_path: Path to the file to process
            user_id: Optional user ID for document ownership
            
        Returns:
            Tuple of (document_id, number of chunks processed)
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Load document
            documents = self.load_document(file_path)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Create metadata for each chunk with user ownership
            metadatas = [{
                "source": file_path,
                "document_id": document_id,
                "chunk_index": i,
                "filename": os.path.basename(file_path),
                "user_id": user_id  # Add user ownership
            } for i in range(len(chunks))]
            
            # Store embeddings in document-specific collection
            self.embedding_service.store_embeddings(
                texts=[chunk.page_content for chunk in chunks],
                metadatas=metadatas,
                collection_name=document_id
            )
            
            logger.info(f"Processed file {file_path}: {len(chunks)} chunks generated for user {user_id}")
            return document_id, len(chunks)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise Exception(f"Error processing file: {str(e)}")

    def process_files_batch(self, file_paths: List[str], file_sizes: List[int], user_id: Optional[str] = None) -> List[Dict]:
        """
        Process multiple files in batch.
        
        Args:
            file_paths: List of file paths to process
            file_sizes: List of corresponding file sizes
            user_id: Optional user ID for document ownership
            
        Returns:
            List of processing results for each file
        """
        results = []
        
        for file_path, file_size in zip(file_paths, file_sizes):
            try:
                # Validate file
                is_valid, error_message = self.validate_file(file_path, file_size)
                
                if not is_valid:
                    results.append({
                        "filename": os.path.basename(file_path),
                        "status": "error",
                        "error_message": error_message,
                        "chunk_count": None,
                        "document_id": None
                    })
                    continue
                
                # Process file with user ownership
                document_id, chunk_count = self.process_file(file_path, user_id)
                
                results.append({
                    "filename": os.path.basename(file_path),
                    "status": "success",
                    "error_message": None,
                    "chunk_count": chunk_count,
                    "document_id": document_id
                })
                
            except Exception as e:
                results.append({
                    "filename": os.path.basename(file_path),
                    "status": "error",
                    "error_message": str(e),
                    "chunk_count": None,
                    "document_id": None
                })
        
        return results 