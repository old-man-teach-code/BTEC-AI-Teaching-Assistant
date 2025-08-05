import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from llama_index.core import VectorStoreIndex, QueryBundle
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode

from core.config import settings
from core.llm_config import get_llm
from core.embedding_config import get_embed_model
from database.vector_store import vector_store_manager
from models.schemas import SearchResult

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service quản lý Retrieval-Augmented Generation (RAG)
    Cung cấp chức năng search và quản lý knowledge base
    """
    
    def __init__(self):
        self.indices: Dict[str, VectorStoreIndex] = {}
        
    def _get_or_create_index(self, collection_name: str) -> VectorStoreIndex:
        """
        Lấy hoặc tạo index cho collection
        
        Args:
            collection_name: Tên collection
            
        Returns:
            VectorStoreIndex instance
        """
        if collection_name not in self.indices:
            # Ensure collection exists
            vector_store_manager._ensure_collection(collection_name)
            
            # Create index từ vector store
            from llama_index.vector_stores.chroma import ChromaVectorStore
            vector_store = ChromaVectorStore(
                chroma_collection=vector_store_manager.collections[collection_name],
                embed_model=get_embed_model()
            )
            
            # Create index
            self.indices[collection_name] = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=get_embed_model()
            )
            
            logger.info(f"Created index for collection: {collection_name}")
        
        return self.indices[collection_name]
    
    async def search(
        self,
        query: str,
        user_id: Optional[int] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Tìm kiếm trong knowledge base
        
        Args:
            query: Query text
            user_id: ID của user (None = search global)
            top_k: Số kết quả tối đa
            filters: Metadata filters
            
        Returns:
            List of SearchResult
        """
        try:
            # Sử dụng vector store manager search
            raw_results = vector_store_manager.search(
                query=query,
                user_id=user_id,
                n_results=top_k,
                filter_metadata=filters
            )
            
            # Convert to SearchResult format
            search_results = []
            for result in raw_results:
                metadata = result.get("metadata", {})
                
                search_result = SearchResult(
                    text=result["text"],
                    score=result["score"],
                    metadata=metadata,
                    source=metadata.get("file_name") or metadata.get("source")
                )
                search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} results for query: '{query[:50]}...'")
            return search_results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    async def query_with_context(
        self,
        query: str,
        user_id: int,
        use_llm: bool = True,
        response_mode: str = "compact"
    ) -> Dict[str, Any]:
        """
        Query với context và optional LLM response synthesis
        
        Args:
            query: Query text
            user_id: ID của user
            use_llm: Có sử dụng LLM để tổng hợp response không
            response_mode: Mode cho response synthesis
            
        Returns:
            Query result với context
        """
        try:
            # Search for relevant chunks
            search_results = await self.search(
                query=query,
                user_id=user_id,
                top_k=settings.top_k_results
            )
            
            if not search_results:
                return {
                    "answer": "Không tìm thấy thông tin liên quan trong knowledge base.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Extract context từ search results
            context_texts = [result.text for result in search_results]
            sources = [result.source for result in search_results if result.source]
            
            # Nếu không dùng LLM, trả về raw results
            if not use_llm:
                return {
                    "answer": None,
                    "context": context_texts,
                    "sources": sources,
                    "raw_results": search_results
                }
            
            # Sử dụng LLM để tổng hợp answer
            llm = get_llm()
            
            # Tạo prompt cho LLM
            context_str = "\n\n".join(context_texts)
            prompt = llm_manager.create_prompt_template(
                instruction="Dựa vào ngữ cảnh được cung cấp, hãy trả lời câu hỏi một cách chính xác và ngắn gọn. Nếu không tìm thấy thông tin trong ngữ cảnh, hãy nói rõ điều đó.",
                context=context_str,
                question=query
            )
            
            # Generate answer
            answer = llm.complete(prompt).text
            
            # Calculate confidence based on search scores
            avg_score = sum(r.score for r in search_results) / len(search_results)
            
            return {
                "answer": answer,
                "sources": list(set(sources)),  # Remove duplicates
                "confidence": avg_score,
                "context_used": len(context_texts)
            }
            
        except Exception as e:
            logger.error(f"Error in query_with_context: {str(e)}")
            return {
                "answer": f"Có lỗi xảy ra khi xử lý câu hỏi: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Lấy thống kê về knowledge base của user
        
        Args:
            user_id: ID của user
            
        Returns:
            Statistics dictionary
        """
        try:
            stats = {
                "total_chunks": 0,
                "last_updated": None,
                "storage_used_mb": 0.0,
                "collections": []
            }
            
            # Check user collection
            user_collection_name = vector_store_manager.get_user_collection_name(user_id)
            user_stats = vector_store_manager.get_collection_stats(user_collection_name)
            
            if "error" not in user_stats:
                stats["collections"].append({
                    "name": user_collection_name,
                    "type": "user",
                    "count": user_stats.get("count", 0)
                })
                stats["total_chunks"] += user_stats.get("count", 0)
            
            # Check global collection for user's documents
            global_collection = vector_store_manager.collections.get(settings.chroma_collection_name)
            if global_collection:
                try:
                    # Query để đếm documents của user trong global collection
                    results = global_collection.query(
                        query_texts=[""],  # Empty query
                        where={"user_id": {"$eq": str(user_id)}},
                        n_results=1,
                        include=[]
                    )
                    
                    # ChromaDB không có direct count với filter, estimate từ query
                    # Trong production nên track riêng hoặc dùng database khác
                    global_count = len(results.get("ids", [[]])[0])
                    
                    stats["collections"].append({
                        "name": settings.chroma_collection_name,
                        "type": "global",
                        "count": global_count
                    })
                    
                except Exception as e:
                    logger.warning(f"Cannot get global stats: {str(e)}")
            
            # Estimate storage (rough calculation)
            # Assume average chunk size ~ 1KB
            stats["storage_used_mb"] = stats["total_chunks"] * 0.001
            
            # Last updated - would need to track this separately
            stats["last_updated"] = datetime.now()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {
                "error": str(e),
                "total_chunks": 0
            }
    
    async def get_document_chunks_count(
        self,
        document_id: int,
        user_id: int
    ) -> int:
        """
        Đếm số chunks của một document
        
        Args:
            document_id: ID của document
            user_id: ID của user
            
        Returns:
            Số chunks
        """
        try:
            # Search với filter document_id
            filter_metadata = {"document_id": str(document_id)}
            
            results = vector_store_manager.search(
                query="",  # Empty query
                user_id=user_id,
                n_results=1000,  # Get all chunks
                filter_metadata=filter_metadata
            )
            
            return len(results)
            
        except Exception as e:
            logger.error(f"Error counting document chunks: {str(e)}")
            return 0
    
    async def delete_documents(
        self,
        user_id: int,
        document_ids: List[int]
    ) -> int:
        """
        Xóa knowledge của specific documents
        
        Args:
            user_id: ID của user
            document_ids: List document IDs cần xóa
            
        Returns:
            Số documents đã xóa
        """
        try:
            deleted_count = 0
            
            for doc_id in document_ids:
                # Generate chunk IDs pattern
                chunk_ids = []
                
                # Estimate max chunks per document (e.g., 1000)
                for i in range(1000):
                    chunk_ids.append(f"doc_{user_id}_{doc_id}_{i}")
                
                # Delete from user collection
                user_collection_name = vector_store_manager.get_user_collection_name(user_id)
                if user_collection_name in vector_store_manager.collections:
                    count = vector_store_manager.delete_documents(
                        document_ids=chunk_ids,
                        collection_name=user_collection_name
                    )
                    if count > 0:
                        deleted_count += 1
                
                # Delete from global collection
                count = vector_store_manager.delete_documents(
                    document_ids=chunk_ids,
                    collection_name=settings.chroma_collection_name
                )
                if count > 0 and deleted_count == 0:
                    deleted_count += 1
            
            logger.info(f"Deleted knowledge for {deleted_count} documents")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return 0
    
    async def clear_user_knowledge(self, user_id: int) -> bool:
        """
        Xóa toàn bộ knowledge của user
        
        Args:
            user_id: ID của user
            
        Returns:
            Success status
        """
        try:
            success = vector_store_manager.clear_user_knowledge(user_id)
            
            # Clear cached indices
            user_collection_name = vector_store_manager.get_user_collection_name(user_id)
            if user_collection_name in self.indices:
                del self.indices[user_collection_name]
            
            return success
            
        except Exception as e:
            logger.error(f"Error clearing user knowledge: {str(e)}")
            return False
    
    async def find_similar_chunks(
        self,
        text: str,
        user_id: int,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Tìm các chunks tương tự với text cho trước
        
        Args:
            text: Text cần tìm similar
            user_id: ID của user
            top_k: Số kết quả tối đa
            threshold: Ngưỡng similarity score tối thiểu
            
        Returns:
            List of similar chunks
        """
        try:
            # Search for similar chunks
            results = await self.search(
                query=text,
                user_id=user_id,
                top_k=top_k
            )
            
            # Filter by threshold
            similar_chunks = []
            for result in results:
                if result.score >= threshold:
                    similar_chunks.append({
                        "text": result.text,
                        "score": result.score,
                        "metadata": result.metadata,
                        "source": result.source
                    })
            
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            return []
    
    def create_context_from_results(
        self,
        search_results: List[SearchResult],
        max_context_length: int = 2000
    ) -> str:
        """
        Tạo context string từ search results
        
        Args:
            search_results: List of search results
            max_context_length: Max length của context
            
        Returns:
            Context string
        """
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results):
            # Format chunk với metadata
            chunk_text = f"[Nguồn: {result.source or 'Unknown'}]\n{result.text}\n"
            chunk_length = len(chunk_text)
            
            # Check length limit
            if current_length + chunk_length > max_context_length:
                # Truncate if needed
                remaining = max_context_length - current_length
                if remaining > 100:  # Only add if meaningful
                    chunk_text = chunk_text[:remaining] + "..."
                    context_parts.append(chunk_text)
                break
            
            context_parts.append(chunk_text)
            current_length += chunk_length
        
        return "\n---\n".join(context_parts)


# Import để tránh circular dependency
from core.llm_config import llm_manager