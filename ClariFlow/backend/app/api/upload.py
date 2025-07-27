import os
import aiofiles
import hashlib
import re
from typing import List
from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from sqlalchemy.orm import Session
from ..services.document_processing import DocumentProcessor
from ..services.audit_service import AuditService
from ..core.database import get_db
from ..models.upload import UploadResponse, FileUploadResult
from ..core.config import settings
from ..core.security import get_current_active_user, verify_api_key_header
from ..models.user import User
from ..utils.logger import setup_logger

router = APIRouter()
processor = DocumentProcessor()
audit_service = AuditService()
logger = setup_logger(__name__)

def validate_file_size(file_size: int) -> bool:
    """Validate file size against maximum allowed size."""
    return file_size <= settings.MAX_FILE_SIZE

def validate_file_extension(filename: str) -> bool:
    """Validate file extension against allowed extensions."""
    if not filename:
        return False
    
    # Get file extension
    _, ext = os.path.splitext(filename.lower())
    return ext in settings.ALLOWED_EXTENSIONS

def sanitize_filename(filename: str, user_id: str) -> str:
    """
    Sanitize filename to prevent path traversal and ensure uniqueness.
    
    Args:
        filename: Original filename
        user_id: User ID for uniqueness
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return f"file_{user_id}_{hashlib.md5(str(os.urandom(16)).encode()).hexdigest()[:8]}"
    
    # Remove path traversal attempts
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    # Ensure uniqueness by adding user ID and hash
    name, ext = os.path.splitext(filename)
    file_hash = hashlib.md5(f"{user_id}_{filename}_{os.urandom(8).hex()}".encode()).hexdigest()[:8]
    
    return f"{user_id}_{name}_{file_hash}{ext}"

def check_file_duplicate(file_path: str, user_id: str, db: Session) -> bool:
    """
    Check if file already exists for the user.
    
    Args:
        file_path: Path to the file
        user_id: User ID
        db: Database session
        
    Returns:
        True if file is duplicate, False otherwise
    """
    try:
        # Check if file exists in uploads directory
        if os.path.exists(file_path):
            # Get file hash for comparison
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Check if this hash already exists for this user
            # This is a simple implementation - in production, you'd want a proper database table
            upload_dir = settings.UPLOAD_DIR
            for existing_file in os.listdir(upload_dir):
                if existing_file.startswith(f"{user_id}_"):
                    existing_path = os.path.join(upload_dir, existing_file)
                    try:
                        with open(existing_path, 'rb') as f:
                            existing_hash = hashlib.md5(f.read()).hexdigest()
                        if existing_hash == file_hash:
                            return True
                    except:
                        continue
            
        return False
    except Exception as e:
        logger.error(f"Error checking file duplicate: {str(e)}")
        return False

@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process multiple document files.
    
    Args:
        files: List of files to upload (PDF, DOCX, TXT, CSV, XLSX, XLS, or MD)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UploadResponse with processing status for each file
        
    Raises:
        HTTPException: If no files provided, file too large, or processing fails
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files provided for upload"
        )
    
    # Validate number of files
    if len(files) > 10:  # Limit to 10 files per request
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum 10 files per request."
        )
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_paths = []
    file_sizes = []
    saved_files = []
    
    try:
        # Validate and save all files
        for file in files:
            # Validate file extension
            if not file.filename or not validate_file_extension(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed: {file.filename}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            if not validate_file_size(file_size):
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large: {file.filename}. Maximum size: {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Sanitize filename
            sanitized_filename = sanitize_filename(file.filename, str(current_user.id))
            file_path = os.path.join(settings.UPLOAD_DIR, sanitized_filename)
            
            # Check for duplicates
            if check_file_duplicate(file_path, str(current_user.id), db):
                logger.warning(f"Duplicate file detected: {file.filename}")
                continue
            
            # Save file
            file_paths.append(file_path)
            file_sizes.append(file_size)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            saved_files.append(file_path)
            
            logger.info(f"Saved file for user {current_user.email}: {sanitized_filename} ({file_size} bytes)")
        
        # Process files in batch
        processing_results = processor.process_files_batch(file_paths, file_sizes, str(current_user.id))
        
        # Convert results to FileUploadResult objects
        file_results = []
        successful_count = 0
        failed_count = 0
        
        for i, result in enumerate(processing_results):
            if result["status"] == "success":
                successful_count += 1
            else:
                failed_count += 1
            
            file_result = FileUploadResult(
                filename=os.path.basename(file_paths[i]) if i < len(file_paths) else "unknown",
                status=result["status"],
                document_id=result.get("document_id"),
                chunks_processed=result.get("chunks_processed", 0),
                error_message=result.get("error_message")
            )
            file_results.append(file_result)
        
        # Log audit event
        try:
            audit_service.log_event(
                db=db,
                user_id=str(current_user.id),
                action="file_upload",
                resource_type="document",
                details={
                    "files_count": len(files),
                    "successful_count": successful_count,
                    "failed_count": failed_count,
                    "file_sizes": file_sizes
                }
            )
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
        
        response = UploadResponse(
            results=file_results,
            total_files=len(files),
            successful_count=successful_count,
            failed_count=failed_count
        )
        
        logger.info(f"Upload completed for user {current_user.email}: {successful_count} successful, {failed_count} failed")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading files for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading files: {str(e)}"
        )
    finally:
        # Clean up any saved files if processing failed
        if 'saved_files' in locals():
            for file_path in saved_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {str(e)}")

@router.post("/upload/single", response_model=UploadResponse)
async def upload_single_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and process a single document file (backward compatibility).
    
    Args:
        file: The file to upload (PDF, DOCX, TXT, CSV, XLSX, XLS, or MD)
        current_user: Current authenticated user
        
    Returns:
        UploadResponse with processing status
        
    Raises:
        HTTPException: If file type is not supported, file too large, or processing fails
    """
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_path = None
    
    try:
        # Validate file extension
        if not file.filename or not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed: {file.filename}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Save file
        sanitized_filename = sanitize_filename(file.filename, str(current_user.id))
        file_path = os.path.join(settings.UPLOAD_DIR, sanitized_filename)
        content = await file.read()
        
        # Validate file size
        if not validate_file_size(len(content)):
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file.filename}. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Saved single file for user {current_user.email}: {sanitized_filename} ({len(content)} bytes)")
        
        # Process file using batch method for consistency
        processing_results = processor.process_files_batch([file_path], [len(content)], str(current_user.id))
        result = processing_results[0]
        
        file_result = FileUploadResult(
            filename=os.path.basename(file_path),
            status=result["status"],
            document_id=result.get("document_id"),
            chunks_processed=result.get("chunks_processed", 0),
            error_message=result.get("error_message")
        )
        
        response = UploadResponse(
            results=[file_result],
            total_files=1,
            successful_count=1 if result["status"] == "success" else 0,
            failed_count=0 if result["status"] == "success" else 1
        )
        
        logger.info(f"Single file upload completed for user {current_user.email}: {result['status']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading single file for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
    finally:
        # Clean up file if processing failed
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {str(e)}")

@router.post("/upload/api-key", response_model=UploadResponse)
async def upload_files_with_api_key(
    files: List[UploadFile] = File(...),
    api_key_valid: bool = Depends(verify_api_key_header)
):
    """
    Upload files using API key authentication (for internal tools).
    
    Args:
        files: List of files to upload
        api_key_valid: Validated API key
        
    Returns:
        UploadResponse with processing status
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files provided for upload"
        )
    
    # Validate number of files
    if len(files) > 5:  # Limit to 5 files per request for API key access
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum 5 files per request for API key access."
        )
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_paths = []
    file_sizes = []
    saved_files = []
    
    try:
        # Validate and save all files
        for file in files:
            # Validate file extension
            if not file.filename or not validate_file_extension(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed: {file.filename}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            if not validate_file_size(file_size):
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large: {file.filename}. Maximum size: {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Sanitize filename for API key uploads
            sanitized_filename = sanitize_filename(file.filename, "api_key")
            file_path = os.path.join(settings.UPLOAD_DIR, sanitized_filename)
            file_paths.append(file_path)
            file_sizes.append(file_size)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            saved_files.append(file_path)
            
            logger.info(f"Saved file via API key: {sanitized_filename} ({file_size} bytes)")
        
        # Process files in batch (use system user ID for API key uploads)
        processing_results = processor.process_files_batch(file_paths, file_sizes, "system")
        
        # Convert results to FileUploadResult objects
        file_results = []
        successful_count = 0
        failed_count = 0
        
        for i, result in enumerate(processing_results):
            if result["status"] == "success":
                successful_count += 1
            else:
                failed_count += 1
            
            file_result = FileUploadResult(
                filename=os.path.basename(file_paths[i]) if i < len(file_paths) else "unknown",
                status=result["status"],
                document_id=result.get("document_id"),
                chunks_processed=result.get("chunks_processed", 0),
                error_message=result.get("error_message")
            )
            file_results.append(file_result)
        
        response = UploadResponse(
            results=file_results,
            total_files=len(files),
            successful_count=successful_count,
            failed_count=failed_count
        )
        
        logger.info(f"API key upload completed: {successful_count} successful, {failed_count} failed")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading files via API key: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading files: {str(e)}"
        )
    finally:
        # Clean up any saved files if processing failed
        if 'saved_files' in locals():
            for file_path in saved_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {str(e)}")

@router.get("/upload/status")
async def get_upload_status(current_user: User = Depends(get_current_active_user)):
    """
    Get upload status and statistics for the current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Upload status and statistics
    """
    try:
        # This would typically return upload statistics for the user
        # For now, returning a placeholder response
        logger.info(f"Upload status requested by user {current_user.email}")
        return {
            "user_id": current_user.id,
            "total_uploads": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "last_upload": None
        }
    except Exception as e:
        logger.error(f"Error getting upload status for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting upload status"
        ) 
