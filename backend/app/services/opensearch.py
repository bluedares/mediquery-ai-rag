"""
OpenSearch Service - Vector Database for RAG
"""

from typing import List, Dict, Optional, Any
from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError, RequestError
import asyncio

from app.config import settings
from app.utils.logger import logger


class OpenSearchService:
    """
    OpenSearch service for vector search and document storage
    
    Features:
    - k-NN vector search
    - Hybrid search (semantic + keyword)
    - Index management
    - Bulk operations
    
    Note: Uses sync client with async wrappers for compatibility
    """
    
    def __init__(self, endpoint: Optional[str] = None):
        """
        Initialize OpenSearch service
        
        Args:
            endpoint: OpenSearch endpoint (defaults to settings)
        """
        self.endpoint = endpoint or settings.opensearch_endpoint
        
        if not self.endpoint:
            logger.warning(
                "⚠️  OpenSearch endpoint not configured",
                message="Using mock mode for development"
            )
            self.client = None
            self.mock_mode = True
            return
        
        self.mock_mode = False
        
        try:
            # Initialize sync client (will wrap in async)
            logger.info(
                "🔧 Initializing OpenSearch client",
                endpoint=self.endpoint,
                username=settings.opensearch_username,
                auth_method="master_user"
            )
            
            self.client = OpenSearch(
                hosts=[self.endpoint],
                http_auth=(settings.opensearch_username, settings.opensearch_password),
                use_ssl=True,
                verify_certs=False,  # TODO: Enable in production
                ssl_show_warn=False
            )
            
            logger.info(
                "✅ OpenSearch client initialized successfully",
                endpoint=self.endpoint,
                username=settings.opensearch_username
            )
        except Exception as e:
            logger.error(
                "❌ Failed to initialize OpenSearch client",
                error=str(e),
                endpoint=self.endpoint
            )
            raise
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run sync function in executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    async def create_index(
        self,
        index_name: str,
        dimension: int = 1024,
        force: bool = False
    ) -> bool:
        """
        Create vector search index
        
        Args:
            index_name: Name of the index
            dimension: Vector dimension
            force: Force recreate if exists
            
        Returns:
            True if successful
        """
        if self.mock_mode:
            logger.info("🔧 Mock mode: Index creation skipped")
            return True
        
        try:
            # Check if index exists
            exists = await self._run_sync(self.client.indices.exists, index=index_name)
            
            if exists:
                if force:
                    await self._run_sync(self.client.indices.delete, index=index_name)
                    logger.info(f"🗑️  Deleted existing index: {index_name}")
                else:
                    logger.info(f"✅ Index already exists: {index_name}")
                    return True
            
            # Index configuration
            body = {
                "settings": {
                    "index.knn": True,
                    "number_of_shards": 3,
                    "number_of_replicas": 2,
                    "index.knn.algo_param.ef_search": 512
                },
                "mappings": {
                    "properties": {
                        "text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": dimension,
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib",
                                "parameters": {
                                    "ef_construction": 512,
                                    "m": 16
                                }
                            }
                        },
                        "metadata": {
                            "properties": {
                                "document_id": {"type": "keyword"},
                                "page": {"type": "integer"},
                                "section": {"type": "keyword"},
                                "chunk_id": {"type": "keyword"},
                                "timestamp": {"type": "date"}
                            }
                        }
                    }
                }
            }
            
            # Create index
            await self._run_sync(self.client.indices.create, index=index_name, body=body)
            
            logger.info(
                "✅ Created index",
                index=index_name,
                dimension=dimension
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "❌ Error creating index",
                error=str(e),
                index=index_name
            )
            raise
    
    def index_document(
        self,
        index_name: str,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Index a single document
        
        Args:
            index_name: Index name
            doc_id: Document ID
            text: Text content
            embedding: Vector embedding
            metadata: Document metadata
            
        Returns:
            True if successful
        """
        if self.mock_mode:
            logger.debug("🔧 Mock mode: Document indexing skipped")
            return True
        
        try:
            body = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {}
            }
            
            self.client.index(
                index=index_name,
                id=doc_id,
                body=body
            )
            
            logger.debug(
                "✅ Indexed document",
                index=index_name,
                doc_id=doc_id
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "❌ Error indexing document",
                error=str(e),
                doc_id=doc_id
            )
            raise
    
    async def vector_search(
        self,
        index_name: str,
        query_embedding: List[float],
        top_k: int = 20,
        filter_query: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform k-NN vector search
        
        Args:
            index_name: Index name
            query_embedding: Query vector
            top_k: Number of results
            filter_query: Optional filter query
            
        Returns:
            List of matching documents
        """
        if self.mock_mode:
            logger.debug("🔧 Mock mode: Returning empty results")
            return []
        
        try:
            # Build k-NN query
            query = {
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": top_k
                        }
                    }
                }
            }
            
            # Add filter if provided
            if filter_query:
                query["query"] = {
                    "bool": {
                        "must": [query["query"]],
                        "filter": filter_query
                    }
                }
            
            # Execute search
            response = await self._run_sync(self.client.search, index=index_name, body=query)
            
            # Extract results
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'text': hit['_source']['text'],
                    'metadata': hit['_source']['metadata']
                })
            
            logger.debug(
                "🔍 Vector search complete",
                index=index_name,
                results=len(results)
            )
            
            return results
            
        except Exception as e:
            logger.error(
                "❌ Error in vector search",
                error=str(e),
                index=index_name
            )
            raise
    
    async def hybrid_search(
        self,
        index_name: str,
        query_text: str,
        query_embedding: List[float],
        top_k: int = 20
    ) -> List[Dict]:
        """
        Hybrid search combining semantic and keyword search
        
        Args:
            index_name: Index name
            query_text: Query text for keyword search
            query_embedding: Query vector for semantic search
            top_k: Number of results
            
        Returns:
            List of matching documents
        """
        if self.mock_mode:
            logger.debug("🔧 Mock mode: Returning mock results")
            return [
                {
                    'id': 'mock_1',
                    'score': 0.95,
                    'text': 'Mock document text for testing',
                    'metadata': {'document_id': 'doc_123', 'page': 1}
                }
            ]
        
        try:
            # Hybrid query
            query = {
                "size": top_k,
                "query": {
                    "hybrid": {
                        "queries": [
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": query_embedding,
                                        "k": top_k
                                    }
                                }
                            },
                            {
                                "match": {
                                    "text": query_text
                                }
                            }
                        ]
                    }
                }
            }
            
            response = await self._run_sync(self.client.search, index=index_name, body=query)
            
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'text': hit['_source']['text'],
                    'metadata': hit['_source']['metadata']
                })
            
            logger.debug(
                "🔍 Hybrid search complete",
                index=index_name,
                results=len(results)
            )
            
            return results
            
        except Exception as e:
            logger.error(
                "❌ Error in hybrid search",
                error=str(e),
                index=index_name
            )
            # Fallback to vector search
            return await self.vector_search(index_name, query_embedding, top_k)
    
    async def health_check(self) -> bool:
        """
        Check if OpenSearch is available
        
        Returns:
            True if service is healthy
        """
        if self.mock_mode:
            return True
        
        try:
            info = await self._run_sync(self.client.info)
            logger.debug(
                "✅ OpenSearch health check passed",
                version=info.get('version', {}).get('number')
            )
            return True
        except Exception as e:
            logger.warning(
                "⚠️  OpenSearch health check failed",
                error=str(e)
            )
            return False


# Global service instance
opensearch_service = OpenSearchService()
