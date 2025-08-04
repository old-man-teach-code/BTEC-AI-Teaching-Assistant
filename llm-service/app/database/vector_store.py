import logging
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.schema import Document as LlamaDocument

from core.config import settings
from core.embedding_config import get_embed_model

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Quản lý Vector Store sử dụng ChromaDB
    Lưu trữ và tìm kiếm knowledge theo user_id
    """
    
    def __init__(self):
        self.chroma_client: Optional[chromadb.Client] = None
        self.vector_store: Optional[ChromaVectorStore] = None
        self.collections: Dict[str, chromadb.Collection] = {}
        
    def initialize(self) -> None:
        """
        Khởi tạo ChromaDB client và collections
        """
        try:
            logger.info("Đang khởi tạo ChromaDB Vector Store...")
            
            # Cấu hình ChromaDB
            chroma_settings = ChromaSettings(
                persist_directory=str(settings.chroma_persist_directory),
                anonymized_telemetry=False,  # Tắt telemetry
                allow_reset=True,  # Cho phép reset database nếu cần
            )
            
            # Khởi tạo ChromaDB client (persistent)
            self.chroma_client = chromadb.PersistentClient(
                path=str(settings.chroma_persist_directory),
                settings=chroma_settings
            )
            
            # Tạo collection chính cho toàn bộ hệ thống
            self._ensure_collection(settings.chroma_collection_name)
            
            logger.info("✅ Vector Store khởi tạo thành công!")
            
            # Test vector store
            self._test_vector_store()
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi tạo Vector Store: {str(e)}")
            raise
    
    def _ensure_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Đảm bảo collection tồn tại, tạo mới nếu chưa có
        
        Args:
            collection_name: Tên collection
            
        Returns:
            ChromaDB Collection
        """
        try:
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Knowledge base for {collection_name}"}
            )
            
            # Cache collection
            self.collections[collection_name] = collection
            
            # Create LlamaIndex vector store wrapper
            if collection_name == settings.chroma_collection_name:
                self.vector_store = ChromaVectorStore(
                    chroma_collection=collection,
                    embed_model=get_embed_model()
                )
            
            logger.info(f"Collection '{collection_name}' sẵn sàng. Số documents: {collection.count()}")
            return collection
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo/lấy collection: {str(e)}")
            raise
    
    def _test_vector_store(self) -> None:
        """Test vector store với sample data"""
        try:
            test_collection = self._ensure_collection("test_collection")
            
            # Add test document
            test_doc = {
                "id": "test_doc_1",
                "text": "Đây là document test cho vector store",
                "metadata": {"source": "test", "user_id": "test_user"}
            }
            
            # Test add
            test_collection.add(
                documents=[test_doc["text"]],
                ids=[test_doc["id"]],
                metadatas=[test_doc["metadata"]]
            )
            
            # Test query
            results = test_collection.query(
                query_texts=["test vector store"],
                n_results=1
            )
            
            logger.info("Test Vector Store thành công!")
            
            # Cleanup test collection
            self.chroma_client.delete_collection("test_collection")
            
        except Exception as e:
            logger.error(f"Test Vector Store thất bại: {str(e)}")
            raise
    
    def get_user_collection_name(self, user_id: int) -> str:
        """
        Tạo tên collection cho user cụ thể
        
        Args:
            user_id: ID của user
            
        Returns:
            Tên collection
        """
        return f"user_{user_id}_knowledge"
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        user_id: Optional[int] = None,
        collection_name: Optional[str] = None
    ) -> List[str]:
        """
        Thêm documents vào vector store
        
        Args:
            documents: List các documents với format:
                      [{"text": "...", "metadata": {...}, "id": "optional_id"}]
            user_id: ID của user (nếu lưu theo user)
            collection_name: Tên collection (nếu không dùng default)
            
        Returns:
            List document IDs đã thêm
        """
        try:
            # Xác định collection
            if collection_name:
                collection = self._ensure_collection(collection_name)
            elif user_id:
                collection = self._ensure_collection(self.get_user_collection_name(user_id))
            else:
                collection = self.collections[settings.chroma_collection_name]
            
            # Prepare data
            texts = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(documents):
                # Text content
                text = doc.get("text", "")
                if not text:
                    logger.warning(f"Document {i} không có text, bỏ qua")
                    continue
                
                texts.append(text)
                
                # Metadata
                metadata = doc.get("metadata", {})
                if user_id and "user_id" not in metadata:
                    metadata["user_id"] = str(user_id)
                metadatas.append(metadata)
                
                # Document ID
                doc_id = doc.get("id", f"doc_{user_id}_{i}_{hash(text)}")
                ids.append(doc_id)
            
            if not texts:
                logger.warning("Không có documents hợp lệ để thêm")
                return []
            
            # Add to ChromaDB
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Đã thêm {len(texts)} documents vào collection '{collection.name}'")
            return ids
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm documents: {str(e)}")
            raise
    
    def search(
        self,
        query: str,
        user_id: Optional[int] = None,
        collection_name: Optional[str] = None,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm documents trong vector store
        
        Args:
            query: Query text
            user_id: ID của user (để search trong knowledge của user đó)
            collection_name: Tên collection
            n_results: Số kết quả tối đa
            filter_metadata: Metadata filters
            
        Returns:
            List kết quả với format: [{"text": "...", "metadata": {...}, "score": 0.9}]
        """
        try:
            # Xác định collection
            if collection_name:
                collection = self._ensure_collection(collection_name)
            elif user_id:
                # Search trong cả user collection và global collection
                results = []
                
                # Search user-specific collection
                user_collection_name = self.get_user_collection_name(user_id)
                if user_collection_name in self.collections:
                    user_results = self._search_collection(
                        self.collections[user_collection_name],
                        query, n_results // 2, filter_metadata
                    )
                    results.extend(user_results)
                
                # Search global collection với filter user_id
                global_filter = filter_metadata or {}
                global_filter["user_id"] = str(user_id)
                global_results = self._search_collection(
                    self.collections[settings.chroma_collection_name],
                    query, n_results // 2, global_filter
                )
                results.extend(global_results)
                
                # Sort by score và limit
                results.sort(key=lambda x: x["score"], reverse=True)
                return results[:n_results]
            else:
                collection = self.collections[settings.chroma_collection_name]
            
            # Search single collection
            return self._search_collection(collection, query, n_results, filter_metadata)
            
        except Exception as e:
            logger.error(f"Lỗi khi search: {str(e)}")
            return []
    
    def _search_collection(
        self,
        collection: chromadb.Collection,
        query: str,
        n_results: int,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search trong một collection cụ thể
        """
        # Build where clause for metadata filtering
        where_clause = None
        if filter_metadata:
            where_clause = {
                "$and": [
                    {key: {"$eq": value}} for key, value in filter_metadata.items()
                ]
            }
        
        # Query ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
            distances = results["distances"][0] if results["distances"] else [0] * len(documents)
            
            for doc, meta, dist in zip(documents, metadatas, distances):
                # Convert distance to similarity score (0-1)
                # ChromaDB uses L2 distance, so smaller is better
                score = 1 / (1 + dist)  # Simple conversion
                
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "score": score
                })
        
        return formatted_results
    
    def delete_documents(
        self,
        document_ids: List[str],
        collection_name: Optional[str] = None
    ) -> int:
        """
        Xóa documents khỏi vector store
        
        Args:
            document_ids: List document IDs cần xóa
            collection_name: Tên collection
            
        Returns:
            Số documents đã xóa
        """
        try:
            collection = self.collections.get(
                collection_name or settings.chroma_collection_name
            )
            
            if not collection:
                logger.warning(f"Collection '{collection_name}' không tồn tại")
                return 0
            
            # Delete documents
            collection.delete(ids=document_ids)
            
            logger.info(f"Đã xóa {len(document_ids)} documents")
            return len(document_ids)
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa documents: {str(e)}")
            return 0
    
    def get_collection_stats(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Lấy thống kê về collection
        
        Args:
            collection_name: Tên collection
            
        Returns:
            Statistics dict
        """
        try:
            collection = self.collections.get(
                collection_name or settings.chroma_collection_name
            )
            
            if not collection:
                return {"error": f"Collection '{collection_name}' không tồn tại"}
            
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_user_knowledge(self, user_id: int) -> bool:
        """
        Xóa toàn bộ knowledge của một user
        
        Args:
            user_id: ID của user
            
        Returns:
            Success status
        """
        try:
            # Xóa user-specific collection nếu có
            user_collection_name = self.get_user_collection_name(user_id)
            if user_collection_name in self.collections:
                self.chroma_client.delete_collection(user_collection_name)
                del self.collections[user_collection_name]
                logger.info(f"Đã xóa collection '{user_collection_name}'")
            
            # Xóa documents của user trong global collection
            global_collection = self.collections[settings.chroma_collection_name]
            global_collection.delete(
                where={"user_id": {"$eq": str(user_id)}}
            )
            
            logger.info(f"Đã xóa toàn bộ knowledge của user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa user knowledge: {str(e)}")
            return False


# Singleton instance
vector_store_manager = VectorStoreManager()


def initialize_vector_store():
    """Initialize Vector Store - được gọi từ main.py"""
    vector_store_manager.initialize()


def get_vector_store() -> ChromaVectorStore:
    """Get Vector Store instance cho dependency injection"""
    if not vector_store_manager.vector_store:
        raise RuntimeError("Vector Store chưa được khởi tạo!")
    return vector_store_manager.vector_store