"""
ChromaDB Service - Lightweight Vector Database for RAG
ALTERNATIVE: Used when OpenSearch is not available
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import os

from app.config import settings
from app.utils.logger import logger


class ChromaDBService:
    """
    ChromaDB service for vector search and document storage
    
    Features:
    - Persistent local vector storage
    - Cosine similarity search
    - Collection management
    - Metadata filtering
    
    Note: Lightweight alternative to OpenSearch for development/testing
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB service
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory or "./chroma_data"
        
        try:
            logger.info(
                "🔧 Initializing ChromaDB client",
                persist_directory=self.persist_directory
            )
            
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info(
                "✅ ChromaDB client initialized successfully",
                persist_directory=self.persist_directory
            )
        except Exception as e:
            logger.error(
                "❌ Failed to initialize ChromaDB client",
                error=str(e),
                persist_directory=self.persist_directory
            )
            raise
    
    def get_or_create_collection(self, collection_name: str) -> Any:
        """
        Get or create a ChromaDB collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection object
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.debug(f"✅ Collection '{collection_name}' ready")
            return collection
        except Exception as e:
            logger.error(f"❌ Failed to get/create collection: {e}")
            raise
    
    def index_document(
        self,
        collection_name: str,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index a document chunk in ChromaDB
        
        Args:
            collection_name: Name of the collection
            doc_id: Unique document ID
            text: Document text
            embedding: Vector embedding
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )
            
            logger.debug(
                "✅ Document indexed",
                collection=collection_name,
                doc_id=doc_id
            )
            return True
            
        except Exception as e:
            logger.error(
                "❌ Failed to index document",
                error=str(e),
                doc_id=doc_id
            )
            return False
    
    async def vector_search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        
        Args:
            collection_name: Name of the collection
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of search results with text, metadata, and scores
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Query ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    # Convert distance to similarity score (1 - distance for cosine)
                    distance = results['distances'][0][i]
                    score = 1 - distance  # Cosine similarity
                    
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': score,
                        'id': results['ids'][0][i]
                    })
            
            logger.info(
                "✅ Vector search complete",
                collection=collection_name,
                results_count=len(formatted_results),
                top_score=formatted_results[0]['score'] if formatted_results else 0
            )
            
            return formatted_results
            
        except Exception as e:
            logger.error(
                "❌ Vector search failed",
                error=str(e),
                collection=collection_name
            )
            return []
    
    async def hybrid_search(
        self,
        collection_name: str,
        query_text: str,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + keyword)
        
        Note: ChromaDB doesn't have built-in hybrid search like OpenSearch,
        so we'll use vector search with optional metadata filtering
        
        Args:
            collection_name: Name of the collection
            query_text: Query text (for future keyword search)
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of search results
        """
        # For ChromaDB, hybrid search is essentially vector search
        # with optional metadata filtering
        return await self.vector_search(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"✅ Collection '{collection_name}' deleted")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete collection: {e}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        Get number of documents in a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
        except Exception as e:
            logger.error(f"❌ Failed to get collection count: {e}")
            return 0


# Global service instance
chromadb_service: Optional[ChromaDBService] = None


def get_chromadb_service() -> ChromaDBService:
    """Get or create ChromaDB service instance"""
    global chromadb_service
    
    if chromadb_service is None:
        if settings.use_chromadb:
            chromadb_service = ChromaDBService()
        else:
            raise RuntimeError("ChromaDB not enabled. Set USE_CHROMADB=true in .env")
    
    return chromadb_service
