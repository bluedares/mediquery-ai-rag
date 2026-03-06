"""
Health Check API - System Status
"""

from fastapi import APIRouter
from datetime import datetime

from app.models.responses import HealthResponse
from app.config import settings
from app.services import bedrock_service, opensearch_service, s3_service, embedding_service
from app.utils.logger import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check for all services
    
    Checks:
    - Bedrock (Claude Sonnet 4.6)
    - OpenSearch (vector database)
    - S3 (document storage)
    - Embedding service
    
    Returns:
        HealthResponse with service statuses
    """
    logger.debug("🏥 Health check requested")
    
    # Check all services
    services = {}
    
    # Bedrock
    try:
        bedrock_healthy = await bedrock_service.health_check()
        services['bedrock'] = 'available' if bedrock_healthy else 'degraded'
    except Exception as e:
        logger.warning(f"Bedrock health check failed: {e}")
        services['bedrock'] = 'unavailable'
    
    # OpenSearch
    try:
        opensearch_healthy = await opensearch_service.health_check()
        services['opensearch'] = 'available' if opensearch_healthy else 'degraded'
    except Exception as e:
        logger.warning(f"OpenSearch health check failed: {e}")
        services['opensearch'] = 'unavailable'
    
    # S3
    try:
        s3_healthy = await s3_service.health_check()
        services['s3'] = 'available' if s3_healthy else 'degraded'
    except Exception as e:
        logger.warning(f"S3 health check failed: {e}")
        services['s3'] = 'unavailable'
    
    # Embedding service
    try:
        embedding_healthy = await embedding_service.health_check()
        services['embeddings'] = 'available' if embedding_healthy else 'degraded'
    except Exception as e:
        logger.warning(f"Embedding service health check failed: {e}")
        services['embeddings'] = 'unavailable'
    
    # Overall status
    all_available = all(status == 'available' for status in services.values())
    overall_status = 'healthy' if all_available else 'degraded'
    
    response = HealthResponse(
        status=overall_status,
        version=settings.app_version,
        timestamp=datetime.now(),
        services=services,
        debug_mode=settings.debug_mode
    )
    
    logger.info(
        "✅ Health check complete",
        status=overall_status,
        services=services
    )
    
    return response
