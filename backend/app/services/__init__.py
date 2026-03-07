"""
Service Layer Package
External service integrations
"""

# Import only the classes, not the global instances
# This prevents AWS initialization on module import
from .bedrock import BedrockService
from .opensearch import OpenSearchService
from .s3 import S3Service
from .embeddings import EmbeddingService

__all__ = [
    "BedrockService",
    "OpenSearchService",
    "S3Service",
    "EmbeddingService",
]
