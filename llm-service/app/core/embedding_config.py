import logging
from typing import Optional, List
import torch
from sentence_transformers import SentenceTransformer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.embeddings import BaseEmbedding

from core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Quản lý Embedding Model cho việc chuyển đổi text thành vectors
    Sử dụng model tiếng Việt: dangvantuan/vietnamese-embedding
    """
    
    def __init__(self):
        self.embed_model: Optional[HuggingFaceEmbedding] = None
        self.raw_model: Optional[SentenceTransformer] = None
        self.device: str = "cpu"
        
    def initialize(self) -> None:
        """
        Khởi tạo Embedding Model
        Model được optimize cho tiếng Việt
        """
        try:
            logger.info(f"Đang khởi tạo Embedding Model: {settings.embedding_model}")
            
            # Xác định device (CPU/GPU)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Sử dụng device: {self.device}")
            
            # Cấu hình model
            model_kwargs = {
                "device": self.device,
                "cache_folder": str(settings.model_cache_dir),
            }
            
            # Khởi tạo raw model (sentence-transformers)
            self.raw_model = SentenceTransformer(
                settings.embedding_model,
                device=self.device,
                cache_folder=str(settings.model_cache_dir)
            )
            
            # Wrap với LlamaIndex interface
            self.embed_model = HuggingFaceEmbedding(
                model_name=settings.embedding_model,
                cache_folder=str(settings.model_cache_dir),
                device=self.device,
                # Cấu hình cho batch processing
                embed_batch_size=32,
                # Normalize embeddings để tính similarity tốt hơn
                normalize=True,
                # Trust remote code nếu model yêu cầu
                trust_remote_code=True
            )
            
            logger.info("✅ Embedding Model khởi tạo thành công!")
            
            # Test model
            self._test_model()
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi tạo Embedding Model: {str(e)}")
            raise
    
    def _test_model(self) -> None:
        """Test model với text tiếng Việt"""
        try:
            test_texts = [
                "Xin chào, đây là test embedding",
                "Deadline nộp bài tập là ngày mai"
            ]
            embeddings = self.embed_texts(test_texts)
            
            # Kiểm tra dimension
            embed_dim = len(embeddings[0])
            logger.info(f"Test Embedding thành công. Dimension: {embed_dim}")
            
            # Tính similarity để test
            similarity = self.compute_similarity(embeddings[0], embeddings[1])
            logger.info(f"Test similarity: {similarity:.4f}")
            
        except Exception as e:
            logger.error(f"Test Embedding thất bại: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Chuyển đổi một đoạn text thành vector embedding
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not self.embed_model:
            raise RuntimeError("Embedding Model chưa được khởi tạo!")
        
        # Clean text
        text = text.strip()
        if not text:
            raise ValueError("Text không được rỗng")
        
        # Generate embedding
        embedding = self.embed_model.get_text_embedding(text)
        
        return embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Chuyển đổi nhiều đoạn text thành vectors (batch processing)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if not self.embed_model:
            raise RuntimeError("Embedding Model chưa được khởi tạo!")
        
        # Clean texts
        texts = [text.strip() for text in texts if text.strip()]
        if not texts:
            return []
        
        # Generate embeddings
        embeddings = self.embed_model.get_text_embedding_batch(texts)
        
        return embeddings
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Tính độ tương đồng giữa 2 embeddings sử dụng cosine similarity
        
        Args:
            embedding1: Vector 1
            embedding2: Vector 2
            
        Returns:
            Similarity score (0-1)
        """
        import numpy as np
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, similarity))
    
    def get_model_info(self) -> dict:
        """Lấy thông tin về embedding model"""
        if not self.embed_model:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "model_name": settings.embedding_model,
            "device": self.device,
            "dimension": self._get_embedding_dimension(),
            "max_length": self._get_max_length()
        }
    
    def _get_embedding_dimension(self) -> int:
        """Lấy dimension của embedding vectors"""
        try:
            if self.raw_model:
                return self.raw_model.get_sentence_embedding_dimension()
            # Fallback: generate test embedding
            test_embed = self.embed_text("test")
            return len(test_embed)
        except:
            return -1
    
    def _get_max_length(self) -> int:
        """Lấy max length cho input text"""
        try:
            if self.raw_model:
                return self.raw_model.max_seq_length
            return 512  # Default for most models
        except:
            return 512
    
    def preprocess_text_for_embedding(self, text: str) -> str:
        """
        Tiền xử lý text trước khi embedding
        Optimize cho tiếng Việt
        
        Args:
            text: Raw input text
            
        Returns:
            Processed text
        """
        # Remove extra whitespaces
        text = " ".join(text.split())
        
        # Truncate if too long (để tránh out of memory)
        max_length = self._get_max_length()
        if len(text) > max_length * 4:  # Ước lượng ~4 chars per token
            text = text[:max_length * 4]
            logger.warning(f"Text bị cắt ngắn do quá dài: {len(text)} chars")
        
        return text


# Singleton instance
embedding_manager = EmbeddingManager()


def initialize_embeddings():
    """Initialize Embeddings - được gọi từ main.py"""
    embedding_manager.initialize()


def get_embed_model() -> BaseEmbedding:
    """Get Embedding Model instance cho dependency injection"""
    if not embedding_manager.embed_model:
        raise RuntimeError("Embedding Model chưa được khởi tạo!")
    return embedding_manager.embed_model