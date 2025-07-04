from fastapi import APIRouter, HTTPException, Depends, Query, Path, Request, Header
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..services.crm_service import CRMService
from ..models.crm import (
    CRMType, WebhookEventType, WebhookPayload, HubSpotWebhookPayload,
    CRMSyncRequest, CRMSyncResponse, CRMConnection, CRMConnectionCreate,
    CRMConnectionUpdate, CRMConnectionList, WebhookVerificationRequest,
    WebhookVerificationResponse
)
from ..utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize service
crm_service = CRMService()

@router.post("/crm/connections", response_model=CRMConnection)
async def create_crm_connection(connection_data: CRMConnectionCreate):
    """
    Create a new CRM connection.
    
    This endpoint allows you to configure connections to external CRM systems
    like HubSpot, Salesforce, Pipedrive, etc.
    
    Example:
    - CRM Type: HubSpot
    - Name: "Main HubSpot Account"
    - API Key: "your-hubspot-api-key"
    - Returns: Connection configuration with ID
    """
    try:
        logger.info(f"Creating CRM connection for {connection_data.crm_type.value}")
        
        # Validate required fields
        if not connection_data.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Connection name is required"
            )
        
        if not connection_data.api_key:
            raise HTTPException(
                status_code=400,
                detail="API key is required for CRM connection"
            )
        
        # Create connection
        connection = await crm_service.create_connection(connection_data)
        
        logger.info(f"Successfully created CRM connection: {connection.name}")
        return connection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CRM connection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create CRM connection: {str(e)}"
        )

@router.get("/crm/connections", response_model=CRMConnectionList)
async def get_crm_connections():
    """
    Get all CRM connections.
    
    Returns a list of all configured CRM connections with their
    status, last sync time, and configuration details.
    """
    try:
        logger.info("Getting all CRM connections")
        
        connections = await crm_service.get_connections()
        
        logger.info(f"Retrieved {connections.total_count} CRM connections")
        return connections
        
    except Exception as e:
        logger.error(f"Error getting CRM connections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get CRM connections: {str(e)}"
        )

@router.get("/crm/connections/{connection_id}", response_model=CRMConnection)
async def get_crm_connection(connection_id: str = Path(..., description="Connection ID")):
    """
    Get a specific CRM connection by ID.
    
    Returns detailed information about a single CRM connection
    including configuration and sync status.
    """
    try:
        logger.info(f"Getting CRM connection: {connection_id}")
        
        connections = await crm_service.get_connections()
        connection = None
        
        for conn in connections.connections:
            if conn.id == connection_id:
                connection = conn
                break
        
        if not connection:
            raise HTTPException(
                status_code=404,
                detail=f"CRM connection with ID {connection_id} not found"
            )
        
        return connection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CRM connection {connection_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get CRM connection: {str(e)}"
        )

@router.put("/crm/connections/{connection_id}", response_model=CRMConnection)
async def update_crm_connection(
    connection_id: str = Path(..., description="Connection ID"),
    update_data: CRMConnectionUpdate = None
):
    """
    Update an existing CRM connection.
    
    Allows updating connection properties like name, API key,
    sync frequency, and active status.
    """
    try:
        logger.info(f"Updating CRM connection: {connection_id}")
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="Update data is required"
            )
        
        # Update connection
        updated_connection = await crm_service.update_connection(connection_id, update_data)
        
        logger.info(f"Successfully updated CRM connection: {connection_id}")
        return updated_connection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating CRM connection {connection_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update CRM connection: {str(e)}"
        )

@router.delete("/crm/connections/{connection_id}")
async def delete_crm_connection(connection_id: str = Path(..., description="Connection ID")):
    """
    Delete a CRM connection.
    
    Permanently removes a CRM connection and its configuration.
    """
    try:
        logger.info(f"Deleting CRM connection: {connection_id}")
        
        # Delete connection
        success = await crm_service.delete_connection(connection_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"CRM connection with ID {connection_id} not found"
            )
        
        logger.info(f"Successfully deleted CRM connection: {connection_id}")
        return {"message": f"CRM connection {connection_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CRM connection {connection_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete CRM connection: {str(e)}"
        )

@router.post("/crm/sync", response_model=CRMSyncResponse)
async def sync_crm_data(sync_request: CRMSyncRequest):
    """
    Sync data with external CRM system.
    
    This endpoint triggers a sync operation with the specified CRM system.
    Can sync all data or specific entity types based on the request.
    
    Example:
    - CRM Type: HubSpot
    - Sync Type: "full"
    - Entity Type: "contacts"
    - Returns: Sync results with count and status
    """
    try:
        logger.info(f"Starting CRM sync for {sync_request.crm_type.value}")
        
        # Validate sync request
        if not sync_request.sync_type:
            raise HTTPException(
                status_code=400,
                detail="Sync type is required"
            )
        
        # Perform sync
        result = await crm_service.sync_crm_data(sync_request)
        
        logger.info(f"CRM sync completed: {result.synced_count} records synced")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing CRM data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync CRM data: {str(e)}"
        )

@router.post("/crm/webhook/{crm_type}")
async def handle_webhook(
    crm_type: CRMType = Path(..., description="CRM type"),
    request: Request = None,
    x_hubspot_signature: Optional[str] = Header(None, alias="X-HubSpot-Signature"),
    x_salesforce_signature: Optional[str] = Header(None, alias="X-Salesforce-Signature")
):
    """
    Handle webhooks from CRM systems.
    
    This endpoint receives webhooks from external CRM systems and processes
    them to update internal data. Supports signature verification for security.
    
    Example:
    - CRM Type: HubSpot
    - Event: Lead created
    - Returns: Processing status and any updates made
    """
    try:
        logger.info(f"Received webhook from {crm_type.value}")
        
        # Get request body
        body = await request.body()
        payload = await request.json()
        
        # Determine signature based on CRM type
        signature = None
        if crm_type == CRMType.HUBSPOT:
            signature = x_hubspot_signature
        elif crm_type == CRMType.SALESFORCE:
            signature = x_salesforce_signature
        
        # Process webhook
        result = await crm_service.handle_webhook(crm_type, payload, signature)
        
        logger.info(f"Successfully processed webhook from {crm_type.value}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook from {crm_type.value}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webhook: {str(e)}"
        )

@router.post("/crm/webhook/verify", response_model=WebhookVerificationResponse)
async def verify_webhook(verification_request: WebhookVerificationRequest):
    """
    Verify webhook configuration with CRM system.
    
    This endpoint helps verify that webhook configuration is correct
    by responding to verification challenges from CRM systems.
    
    Example:
    - CRM Type: HubSpot
    - Challenge: "verification_challenge_string"
    - Returns: Verification response
    """
    try:
        logger.info(f"Verifying webhook for {verification_request.crm_type.value}")
        
        # Verify webhook
        result = await crm_service.verify_webhook(verification_request)
        
        logger.info(f"Webhook verification completed for {verification_request.crm_type.value}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify webhook: {str(e)}"
        )

@router.get("/crm/supported-platforms")
async def get_supported_crm_platforms():
    """
    Get list of supported CRM platforms.
    
    Returns information about CRM platforms that can be integrated
    with their capabilities and requirements.
    """
    try:
        supported_platforms = [
            {
                "type": CRMType.HUBSPOT.value,
                "name": "HubSpot",
                "description": "All-in-one CRM platform for marketing, sales, and customer service",
                "capabilities": [
                    "Contact management",
                    "Deal tracking",
                    "Email marketing",
                    "Lead scoring",
                    "Analytics and reporting"
                ],
                "webhook_support": True,
                "api_rate_limit": "100 requests per 10 seconds",
                "required_fields": ["api_key", "portal_id"]
            },
            {
                "type": CRMType.SALESFORCE.value,
                "name": "Salesforce",
                "description": "Cloud-based CRM platform for sales, service, and marketing",
                "capabilities": [
                    "Lead and opportunity management",
                    "Account and contact management",
                    "Sales forecasting",
                    "Workflow automation",
                    "Advanced analytics"
                ],
                "webhook_support": True,
                "api_rate_limit": "1500 requests per 24 hours",
                "required_fields": ["api_key", "instance_url"]
            },
            {
                "type": CRMType.PIPEDRIVE.value,
                "name": "Pipedrive",
                "description": "Sales CRM focused on pipeline management and deal tracking",
                "capabilities": [
                    "Pipeline management",
                    "Deal tracking",
                    "Activity management",
                    "Email integration",
                    "Sales reporting"
                ],
                "webhook_support": True,
                "api_rate_limit": "100 requests per 10 seconds",
                "required_fields": ["api_key"]
            },
            {
                "type": CRMType.NOTION.value,
                "name": "Notion",
                "description": "All-in-one workspace for notes, docs, and project management",
                "capabilities": [
                    "Database management",
                    "Project tracking",
                    "Knowledge base",
                    "Team collaboration",
                    "Custom workflows"
                ],
                "webhook_support": False,
                "api_rate_limit": "3 requests per second",
                "required_fields": ["api_key", "database_id"]
            },
            {
                "type": CRMType.AIRTABLE.value,
                "name": "Airtable",
                "description": "Spreadsheet-database hybrid for organizing and tracking data",
                "capabilities": [
                    "Database management",
                    "Project tracking",
                    "Team collaboration",
                    "Automation",
                    "Custom views"
                ],
                "webhook_support": True,
                "api_rate_limit": "5 requests per second",
                "required_fields": ["api_key", "base_id"]
            },
            {
                "type": CRMType.CUSTOM.value,
                "name": "Custom CRM",
                "description": "Integration with custom or proprietary CRM systems",
                "capabilities": [
                    "Custom data sync",
                    "Flexible mapping",
                    "API integration",
                    "Webhook support"
                ],
                "webhook_support": True,
                "api_rate_limit": "Varies by implementation",
                "required_fields": ["api_url", "api_key"]
            }
        ]
        
        return {"platforms": supported_platforms}
        
    except Exception as e:
        logger.error(f"Error getting supported CRM platforms: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported CRM platforms: {str(e)}"
        )

@router.get("/crm/sync-status")
async def get_sync_status():
    """
    Get sync status for all CRM connections.
    
    Returns the current sync status, last sync time, and any
    pending sync operations for all configured connections.
    """
    try:
        logger.info("Getting CRM sync status")
        
        connections = await crm_service.get_connections()
        
        sync_status = {
            "total_connections": connections.total_count,
            "active_connections": len([c for c in connections.connections if c.is_active]),
            "connections": []
        }
        
        for connection in connections.connections:
            status_info = {
                "id": connection.id,
                "name": connection.name,
                "crm_type": connection.crm_type.value,
                "is_active": connection.is_active,
                "last_sync": connection.last_sync.isoformat() if connection.last_sync else None,
                "sync_frequency": connection.sync_frequency,
                "status": "active" if connection.is_active else "inactive"
            }
            sync_status["connections"].append(status_info)
        
        return sync_status
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )

@router.get("/crm/health")
async def crm_health_check():
    """
    Health check for CRM integration.
    
    Returns the health status of CRM integration services
    and connection status.
    """
    try:
        logger.info("Performing CRM health check")
        
        connections = await crm_service.get_connections()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "CRM Integration",
            "version": "1.0.0",
            "connections": {
                "total": connections.total_count,
                "active": len([c for c in connections.connections if c.is_active]),
                "inactive": len([c for c in connections.connections if not c.is_active])
            },
            "features": {
                "webhook_support": True,
                "sync_support": True,
                "multi_crm_support": True,
                "signature_verification": True
            },
            "supported_crm_types": [crm_type.value for crm_type in CRMType]
        }
        
        logger.info("CRM health check completed successfully")
        return health_status
        
    except Exception as e:
        logger.error(f"CRM health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service": "CRM Integration",
            "error": str(e)
        }
 