import os
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, UploadFile, HTTPException, File, Depends, status, Request
from sqlalchemy.orm import Session
from ..services.document_processing import DocumentProcessor
from ..services.audit_service import AuditService
from ..core.database import get_db
from ..models.upload import UploadResponse, FileUploadResult, UploadStatus
from ..core.config import settings
from ..core.security import get_current_active_user, verify_api_key_header, optional_api_key_auth
from ..middleware.security import rate_limit_per_minute
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
    file_ext = os.path.splitext(filename)[1].lower()
    return file_ext in settings.ALLOWED_EXTENSIONS

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
            
            # Save file
            file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{file.filename}")
            file_paths.append(file_path)
            file_sizes.append(file_size)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            saved_files.append(file_path)
            
            logger.info(f"Saved file for user {current_user.email}: {file.filename} ({file_size} bytes)")
        
        # Process files in batch
        processing_results = processor.process_files_batch(file_paths, file_sizes, str(current_user.id))
        
        # Convert results to FileUploadResult objects
        file_results = []
        successful_count = 0
        failed_count = 0
        
        for result in processing_results:
            file_result = FileUploadResult(
                filename=result["filename"],
                status=UploadStatus(result["status"]),
                error_message=result["error_message"],
                chunk_count=result["chunk_count"],
                document_id=result["document_id"]
            )
            file_results.append(file_result)
            
            if result["status"] == "success":
                successful_count += 1
                # Log successful file upload
                audit_service.log_data_modification_event(
                    db=db,
                    user_id=str(current_user.id),
                    resource_type="document",
                    resource_id=result["document_id"],
                    action="file_upload_success",
                    new_data={
                        "filename": result["filename"],
                        "file_size": result.get("file_size"),
                        "chunk_count": result["chunk_count"]
                    }
                )
            else:
                failed_count += 1
                # Log failed file upload
                audit_service.log_data_modification_event(
                    db=db,
                    user_id=str(current_user.id),
                    resource_type="document",
                    resource_id=result.get("document_id", "unknown"),
                    action="file_upload_failed",
                    new_data={
                        "filename": result["filename"],
                        "error": result["error_message"]
                    }
                )
        
        # Determine overall message
        if successful_count == len(files):
            message = f"All {len(files)} files processed successfully"
        elif successful_count > 0:
            message = f"{successful_count} out of {len(files)} files processed successfully"
        else:
            message = f"Failed to process any of the {len(files)} files"
        
        logger.info(f"Upload completed for user {current_user.email}: {message}")
        
        return UploadResponse(
            message=message,
            total_files=len(files),
            successful_uploads=successful_count,
            failed_uploads=failed_count,
            results=file_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch upload processing for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )
    
    finally:
        # Clean up temporary files
        for file_path in saved_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {str(e)}")

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
        file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{file.filename}")
        content = await file.read()
        
        # Validate file size
        if not validate_file_size(len(content)):
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file.filename}. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Saved single file for user {current_user.email}: {file.filename} ({len(content)} bytes)")
        
        # Process file using batch method for consistency
        processing_results = processor.process_files_batch([file_path], [len(content)], str(current_user.id))
        result = processing_results[0]
        
        file_result = FileUploadResult(
            filename=result["filename"],
            status=UploadStatus(result["status"]),
            error_message=result["error_message"],
            chunk_count=result["chunk_count"],
            document_id=result["document_id"]
        )
        
        if result["status"] == "success":
            message = "File processed successfully"
            successful_count = 1
            failed_count = 0
        else:
            message = f"Failed to process file: {result['error_message']}"
            successful_count = 0
            failed_count = 1
        
        logger.info(f"Single upload completed for user {current_user.email}: {message}")
        
        return UploadResponse(
            message=message,
            total_files=1,
            successful_uploads=successful_count,
            failed_uploads=failed_count,
            results=[file_result]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing single file for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {str(e)}")

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
            
            # Save file
            file_path = os.path.join(settings.UPLOAD_DIR, f"api_key_{file.filename}")
            file_paths.append(file_path)
            file_sizes.append(file_size)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            saved_files.append(file_path)
            
            logger.info(f"Saved file via API key: {file.filename} ({file_size} bytes)")
        
        # Process files in batch (use system user ID for API key uploads)
        processing_results = processor.process_files_batch(file_paths, file_sizes, "system")
        
        # Convert results to FileUploadResult objects
        file_results = []
        successful_count = 0
        failed_count = 0
        
        for result in processing_results:
            file_result = FileUploadResult(
                filename=result["filename"],
                status=UploadStatus(result["status"]),
                error_message=result["error_message"],
                chunk_count=result["chunk_count"],
                document_id=result["document_id"]
            )
            file_results.append(file_result)
            
            if result["status"] == "success":
                successful_count += 1
            else:
                failed_count += 1
        
        # Determine overall message
        if successful_count == len(files):
            message = f"All {len(files)} files processed successfully via API key"
        elif successful_count > 0:
            message = f"{successful_count} out of {len(files)} files processed successfully via API key"
        else:
            message = f"Failed to process any of the {len(files)} files via API key"
        
        logger.info(f"API key upload completed: {message}")
        
        return UploadResponse(
            message=message,
            total_files=len(files),
            successful_uploads=successful_count,
            failed_uploads=failed_count,
            results=file_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in API key upload processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )
    
    finally:
        # Clean up temporary files
        for file_path in saved_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {str(e)}")

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
