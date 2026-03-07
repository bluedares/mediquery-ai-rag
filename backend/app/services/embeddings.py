"""
Embedding Service - HuggingFace Sentence Transformers
"""

import asyncio
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np

from ..config import settings
from ..utils.logger import logger


class EmbeddingService:
    """
    Embedding service using HuggingFace Sentence Transformers
    
    Features:
    - Async embedding generation
    - Batch processing
    - Caching support
    - Normalization
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding service
        
        Args:
            model_name: HuggingFace model name (defaults to settings)
        """
        self.model_name = model_name or settings.embedding_model
        self.dimension = settings.embedding_dimension
        self.batch_size = settings.embedding_batch_size
        
        logger.info(
            "📦 Loading embedding model",
            model=self.model_name,
            dimension=self.dimension
        )
        
        try:
            # Load model
            self.model = SentenceTransformer(self.model_name)
            
            logger.info(
                "✅ Embedding model loaded",
                model=self.model_name,
                max_seq_length=self.model.max_seq_length
            )
        except Exception as e:
            logger.error(
                "❌ Failed to load embedding model",
                error=str(e),
                model=self.model_name
            )
            raise
    
    async def encode(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for texts asynchronously
        
        Args:
            texts: List of text strings
            normalize: Normalize embeddings to unit length
            show_progress: Show progress bar
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        logger.debug(
            "🔢 Generating embeddings",
            num_texts=len(texts),
            model=self.model_name
        )
        
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=show_progress,
                    normalize_embeddings=normalize,
                    convert_to_numpy=True
                )
            )
            
            # Convert to list
            embeddings_list = embeddings.tolist()
            
            logger.debug(
                "✅ Embeddings generated",
                num_embeddings=len(embeddings_list),
                dimension=len(embeddings_list[0]) if embeddings_list else 0
            )
            
            return embeddings_list
            
        except Exception as e:
            logger.error(
                "❌ Error generating embeddings",
                error=str(e),
                num_texts=len(texts)
            )
            raise
    
    async def encode_single(self, text: str, normalize: bool = True) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            normalize: Normalize embedding
            
        Returns:
            Embedding vector
        """
        embeddings = await self.encode([text], normalize=normalize)
        return embeddings[0] if embeddings else []
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        return float(similarity)
    
    async def health_check(self) -> bool:
        """
        Check if embedding service is working
        
        Returns:
            True if service is healthy
        """
        try:
            # Test embedding
            await self.encode_single("Test")
            return True
        except Exception as e:
            logger.warning(
                "⚠️  Embedding service health check failed",
                error=str(e)
            )
            return False


# Global service instance
# Commented out to prevent initialization on import - instantiate when needed
# embedding_service = EmbeddingService()
