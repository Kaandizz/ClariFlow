import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import Request

from ..models.workflow import AuditLog, AuditLogLevel, AuditLogCategory
from ..models.user import User

logger = logging.getLogger(__name__)

class AuditService:
    """Service for managing audit logs"""
    
    def log_event(
        self,
        db: Session,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLogLevel = AuditLogLevel.INFO,
        category: AuditLogCategory = AuditLogCategory.USER_ACTION,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log an audit event"""
        try:
            # Extract request information if available
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.headers.get("user-agent")
            
            audit_log = AuditLog(
                user_id=user_id,
                category=category,
                level=level,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.utcnow()
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            # Also log to application logger
            log_message = f"Audit: {action} by user {user_id} on {resource_type}:{resource_id}"
            if level == AuditLogLevel.ERROR:
                logger.error(log_message)
            elif level == AuditLogLevel.WARNING:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            # Don't raise the exception to avoid breaking the main flow
            return None
    
    def log_authentication_event(
        self,
        db: Session,
        user_id: Optional[str],
        action: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log authentication-related events"""
        level = AuditLogLevel.INFO if success else AuditLogLevel.WARNING
        return self.log_event(
            db=db,
            user_id=user_id,
            action=action,
            resource_type="authentication",
            details={"success": success, **(details or {})},
            level=level,
            category=AuditLogCategory.AUTHENTICATION,
            request=request
        )
    
    def log_data_access_event(
        self,
        db: Session,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log data access events"""
        return self.log_event(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            category=AuditLogCategory.DATA_ACCESS,
            request=request
        )
    
    def log_data_modification_event(
        self,
        db: Session,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log data modification events"""
        details = {}
        if old_data:
            details["old_data"] = old_data
        if new_data:
            details["new_data"] = new_data
        
        return self.log_event(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            category=AuditLogCategory.DATA_MODIFICATION,
            request=request
        )
    
    def log_workflow_event(
        self,
        db: Session,
        user_id: str,
        workflow_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log workflow-related events"""
        return self.log_event(
            db=db,
            user_id=user_id,
            action=action,
            resource_type="workflow",
            resource_id=workflow_id,
            details=details,
            category=AuditLogCategory.WORKFLOW,
            request=request
        )
    
    def log_security_event(
        self,
        db: Session,
        user_id: Optional[str],
        action: str,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLogLevel = AuditLogLevel.WARNING,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log security-related events"""
        return self.log_event(
            db=db,
            user_id=user_id,
            action=action,
            resource_type="security",
            details=details,
            level=level,
            category=AuditLogCategory.SECURITY,
            request=request
        )
    
    def log_system_event(
        self,
        db: Session,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLogLevel = AuditLogLevel.INFO,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log system-level events"""
        return self.log_event(
            db=db,
            user_id=None,  # System events don't have a user
            action=action,
            resource_type="system",
            details=details,
            level=level,
            category=AuditLogCategory.SYSTEM,
            request=request
        )
    
    def get_user_audit_logs(
        self,
        db: Session,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        category: Optional[AuditLogCategory] = None,
        level: Optional[AuditLogLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if category:
            query = query.filter(AuditLog.category == category)
        
        if level:
            query = query.filter(AuditLog.level == level)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    def get_resource_audit_logs(
        self,
        db: Session,
        resource_type: str,
        resource_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs for a specific resource"""
        query = db.query(AuditLog).filter(
            and_(AuditLog.resource_type == resource_type, AuditLog.resource_id == resource_id)
        )
        
        return query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    def get_system_audit_logs(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0,
        level: Optional[AuditLogLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get system-level audit logs"""
        query = db.query(AuditLog).filter(AuditLog.category == AuditLogCategory.SYSTEM)
        
        if level:
            query = query.filter(AuditLog.level == level)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    def get_security_audit_logs(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0,
        level: Optional[AuditLogLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get security-related audit logs"""
        query = db.query(AuditLog).filter(AuditLog.category == AuditLogCategory.SECURITY)
        
        if level:
            query = query.filter(AuditLog.level == level)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    def get_audit_summary(
        self,
        db: Session,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit log summary statistics"""
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        total_logs = query.count()
        
        # Count by category
        category_counts = {}
        for category in AuditLogCategory:
            count = query.filter(AuditLog.category == category).count()
            category_counts[category.value] = count
        
        # Count by level
        level_counts = {}
        for level in AuditLogLevel:
            count = query.filter(AuditLog.level == level).count()
            level_counts[level.value] = count
        
        # Most common actions
        from sqlalchemy import func
        action_counts = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(query.whereclause).group_by(AuditLog.action).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        return {
            "total_logs": total_logs,
            "category_counts": category_counts,
            "level_counts": level_counts,
            "top_actions": [{"action": action, "count": count} for action, count in action_counts],
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else "unknown"
    
    def cleanup_old_logs(self, db: Session, days_to_keep: int = 90) -> int:
        """Clean up old audit logs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Keep critical and security logs longer
            critical_cutoff = datetime.utcnow() - timedelta(days=365)
            
            # Delete old non-critical logs
            deleted_count = db.query(AuditLog).filter(
                and_(
                    AuditLog.created_at < cutoff_date,
                    AuditLog.level != AuditLogLevel.CRITICAL,
                    AuditLog.category != AuditLogCategory.SECURITY
                )
            ).delete()
            
            # Delete old critical logs
            critical_deleted = db.query(AuditLog).filter(
                and_(
                    AuditLog.created_at < critical_cutoff,
                    AuditLog.level == AuditLogLevel.CRITICAL
                )
            ).delete()
            
            db.commit()
            
            total_deleted = deleted_count + critical_deleted
            logger.info(f"Cleaned up {total_deleted} old audit logs")
            
            return total_deleted
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up audit logs: {str(e)}")
            raise 