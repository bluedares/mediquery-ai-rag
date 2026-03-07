"""
Service Layer Package
External service integrations
"""

from .bedrock import bedrock_service, BedrockService
from .opensearch import opensearch_service, OpenSearchService
from .s3 import s3_service, S3Service
from .embeddings import embedding_service, EmbeddingService

__all__ = [
    "bedrock_service",
    "BedrockService",
    "opensearch_service",
    "OpenSearchService",
    "s3_service",
    "S3Service",
    "embedding_service",
    "EmbeddingService",
]
