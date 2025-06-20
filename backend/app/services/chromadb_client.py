import chromadb
from chromadb.config import Settings as ChromaSettings
from core.config import settings
import logging
from typing import Dict, List, Optional, Union
import os

# Thiết lập logging
logger = logging.getLogger(__name__)

class ChromaDBClient:
    """
    Client kết nối và tương tác với ChromaDB
    """
    _instance = None
    
    def __new__(cls):
        """
        Đảm bảo chỉ có một instance của ChromaDBClient (Singleton pattern)
        """
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        Khởi tạo kết nối với ChromaDB
        """
        try:
            # Kiểm tra và tạo thư mục persistent nếu cần
            if settings.CHROMA_USE_PERSISTENT:
                os.makedirs(settings.CHROMA_PERSISTENT_DIR, exist_ok=True)
                
                try:
                    # Khởi tạo client với persistent storage
                    self.client = chromadb.PersistentClient(
                        path=settings.CHROMA_PERSISTENT_DIR,
                        settings=ChromaSettings(
                            chroma_api_impl="rest",
                            chroma_server_host=settings.CHROMA_HOST,
                            chroma_server_http_port=settings.CHROMA_PORT
                        )
                    )
                    logger.info(f"Đã kết nối ChromaDB với persistent storage tại {settings.CHROMA_PERSISTENT_DIR}")
                    self.mock_mode = False
                except Exception as e:
                    logger.warning(f"Không thể kết nối đến ChromaDB server, chuyển sang chế độ mock: {str(e)}")
                    self.mock_mode = True
                    self.mock_collections = {}
            else:
                try:
                    # Khởi tạo client với in-memory storage
                    self.client = chromadb.Client(
                        settings=ChromaSettings(
                            chroma_api_impl="rest",
                            chroma_server_host=settings.CHROMA_HOST,
                            chroma_server_http_port=settings.CHROMA_PORT
                        )
                    )
                    logger.info("Đã kết nối ChromaDB với in-memory storage")
                    self.mock_mode = False
                except Exception as e:
                    logger.warning(f"Không thể kết nối đến ChromaDB server, chuyển sang chế độ mock: {str(e)}")
                    self.mock_mode = True
                    self.mock_collections = {}
                
        except Exception as e:
            logger.error(f"Lỗi kết nối ChromaDB: {str(e)}")
            self.mock_mode = True
            self.mock_collections = {}
    
    def list_collections(self) -> List[str]:
        """
        Liệt kê tất cả các collections trong ChromaDB
        
        Returns:
            List[str]: Danh sách tên các collections
        """
        try:
            if self.mock_mode:
                logger.info("Đang sử dụng chế độ mock cho list_collections")
                return list(self.mock_collections.keys())
                
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            logger.error(f"Lỗi khi liệt kê collections: {str(e)}")
            if not hasattr(self, 'mock_collections'):
                self.mock_collections = {}
            return list(self.mock_collections.keys())
    
    def create_teacher_collection(self, teacher_id: str) -> Dict:
        """
        Tạo collection cho giảng viên dựa trên teacher_id
        
        Args:
            teacher_id (str): ID của giảng viên
            
        Returns:
            Dict: Thông tin về collection đã tạo
        """
        try:
            collection_name = f"teacher_{teacher_id}"
            
            if self.mock_mode:
                logger.info(f"Đang sử dụng chế độ mock cho create_teacher_collection: {collection_name}")
                if collection_name in self.mock_collections:
                    return {"status": "exists", "collection_name": collection_name}
                
                self.mock_collections[collection_name] = {
                    "metadata": {"teacher_id": teacher_id},
                    "documents": []
                }
                
                return {
                    "status": "created", 
                    "collection_name": collection_name,
                    "metadata": {"teacher_id": teacher_id}
                }
            
            # Kiểm tra xem collection đã tồn tại chưa
            existing_collections = self.list_collections()
            if collection_name in existing_collections:
                logger.info(f"Collection {collection_name} đã tồn tại")
                return {"status": "exists", "collection_name": collection_name}
            
            # Tạo collection mới
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"teacher_id": teacher_id}
            )
            
            logger.info(f"Đã tạo collection {collection_name} cho giảng viên {teacher_id}")
            return {
                "status": "created", 
                "collection_name": collection_name,
                "metadata": {"teacher_id": teacher_id}
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo collection cho giảng viên {teacher_id}: {str(e)}")
            if not hasattr(self, 'mock_collections'):
                self.mock_collections = {}
                
            collection_name = f"teacher_{teacher_id}"
            self.mock_collections[collection_name] = {
                "metadata": {"teacher_id": teacher_id},
                "documents": []
            }
            
            return {
                "status": "created (mock)", 
                "collection_name": collection_name,
                "metadata": {"teacher_id": teacher_id}
            }
    
    def get_teacher_collection(self, teacher_id: str):
        """
        Lấy collection của giảng viên dựa trên teacher_id
        
        Args:
            teacher_id (str): ID của giảng viên
            
        Returns:
            Collection: Collection của giảng viên hoặc None nếu không tồn tại
        """
        try:
            collection_name = f"teacher_{teacher_id}"
            
            if self.mock_mode:
                logger.info(f"Đang sử dụng chế độ mock cho get_teacher_collection: {collection_name}")
                if collection_name in self.mock_collections:
                    return self.mock_collections[collection_name]
                return None
                
            return self.client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Lỗi khi lấy collection của giảng viên {teacher_id}: {str(e)}")
            return None
    
    def delete_teacher_collection(self, teacher_id: str) -> bool:
        """
        Xóa collection của giảng viên
        
        Args:
            teacher_id (str): ID của giảng viên
            
        Returns:
            bool: True nếu xóa thành công, False nếu không
        """
        try:
            collection_name = f"teacher_{teacher_id}"
            
            if self.mock_mode:
                logger.info(f"Đang sử dụng chế độ mock cho delete_teacher_collection: {collection_name}")
                if collection_name in self.mock_collections:
                    del self.mock_collections[collection_name]
                    return True
                return False
                
            self.client.delete_collection(name=collection_name)
            logger.info(f"Đã xóa collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa collection của giảng viên {teacher_id}: {str(e)}")
            return False

# Tạo instance để sử dụng trong ứng dụng
chromadb_client = ChromaDBClient() 