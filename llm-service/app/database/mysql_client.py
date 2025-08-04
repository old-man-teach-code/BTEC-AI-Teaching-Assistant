import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from core.config import settings

logger = logging.getLogger(__name__)


class MySQLClient:
    """
    MySQL Client để kết nối với Backend Database
    Chỉ đọc dữ liệu, không ghi (read-only access)
    """
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        
    def initialize(self) -> None:
        """
        Khởi tạo connection pool đến MySQL
        """
        try:
            logger.info("Đang kết nối đến MySQL Backend Database...")
            
            # Tạo engine với connection pool
            self.engine = create_engine(
                settings.mysql_url,
                pool_size=5,  # Số connections trong pool
                max_overflow=10,  # Số connections tối đa có thể tạo thêm
                pool_timeout=30,  # Timeout khi chờ connection từ pool
                pool_recycle=3600,  # Recycle connections sau 1 giờ
                echo=settings.log_level == "DEBUG"  # Log SQL queries nếu DEBUG mode
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Kết nối MySQL thành công!")
            
            # Tạo session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi kết nối MySQL: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager để lấy database session
        Tự động close session sau khi sử dụng
        """
        if not self.SessionLocal:
            raise RuntimeError("MySQL chưa được khởi tạo!")
        
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin user từ database
        
        Args:
            user_id: ID của user
            
        Returns:
            User info dict hoặc None
        """
        try:
            with self.get_session() as session:
                result = session.execute(
                    text("SELECT id, name, email, created_at FROM users WHERE id = :user_id"),
                    {"user_id": user_id}
                ).fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "email": result[2],
                        "created_at": result[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy user info: {str(e)}")
            return None
    
    def get_user_documents(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy danh sách documents của user
        
        Args:
            user_id: ID của user
            limit: Số documents tối đa
            
        Returns:
            List documents
        """
        try:
            with self.get_session() as session:
                query = """
                    SELECT id, filename, original_name, file_path, file_type, 
                           status, created_at, folder_id
                    FROM documents 
                    WHERE owner_id = :user_id 
                      AND is_deleted = FALSE
                      AND status IN ('uploaded', 'ready')
                    ORDER BY created_at DESC
                    LIMIT :limit
                """
                
                results = session.execute(
                    text(query),
                    {"user_id": user_id, "limit": limit}
                ).fetchall()
                
                documents = []
                for row in results:
                    documents.append({
                        "id": row[0],
                        "filename": row[1],
                        "original_name": row[2],
                        "file_path": row[3],
                        "file_type": row[4],
                        "status": row[5],
                        "created_at": row[6],
                        "folder_id": row[7]
                    })
                
                return documents
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy documents: {str(e)}")
            return []
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin document theo ID
        
        Args:
            document_id: ID của document
            
        Returns:
            Document info hoặc None
        """
        try:
            with self.get_session() as session:
                query = """
                    SELECT d.id, d.filename, d.original_name, d.file_path, 
                           d.file_type, d.status, d.created_at, d.owner_id,
                           u.name as owner_name, u.email as owner_email
                    FROM documents d
                    JOIN users u ON d.owner_id = u.id
                    WHERE d.id = :doc_id AND d.is_deleted = FALSE
                """
                
                result = session.execute(
                    text(query),
                    {"doc_id": document_id}
                ).fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "filename": result[1],
                        "original_name": result[2],
                        "file_path": result[3],
                        "file_type": result[4],
                        "status": result[5],
                        "created_at": result[6],
                        "owner_id": result[7],
                        "owner_name": result[8],
                        "owner_email": result[9]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy document: {str(e)}")
            return None
    
    def get_user_templates(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Lấy danh sách templates của user
        
        Args:
            user_id: ID của user
            
        Returns:
            List templates
        """
        try:
            with self.get_session() as session:
                query = """
                    SELECT id, name, content, category, variables, created_at
                    FROM templates
                    WHERE owner_id = :user_id
                    ORDER BY created_at DESC
                """
                
                results = session.execute(
                    text(query),
                    {"user_id": user_id}
                ).fetchall()
                
                templates = []
                for row in results:
                    templates.append({
                        "id": row[0],
                        "name": row[1],
                        "content": row[2],
                        "category": row[3],
                        "variables": row[4],  # JSON field
                        "created_at": row[5]
                    })
                
                return templates
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy templates: {str(e)}")
            return []
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy template theo ID
        
        Args:
            template_id: ID của template
            
        Returns:
            Template info hoặc None
        """
        try:
            with self.get_session() as session:
                query = """
                    SELECT id, name, content, category, variables, 
                           owner_id, created_at
                    FROM templates
                    WHERE id = :template_id
                """
                
                result = session.execute(
                    text(query),
                    {"template_id": template_id}
                ).fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "content": result[2],
                        "category": result[3],
                        "variables": result[4],
                        "owner_id": result[5],
                        "created_at": result[6]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy template: {str(e)}")
            return None
    
    def update_document_status(self, document_id: int, status: str) -> bool:
        """
        Cập nhật status của document (chỉ dùng khi cần thiết)
        
        Args:
            document_id: ID của document
            status: Status mới (processing, ready, error)
            
        Returns:
            Success status
        """
        try:
            with self.get_session() as session:
                query = """
                    UPDATE documents 
                    SET status = :status, updated_at = NOW()
                    WHERE id = :doc_id
                """
                
                session.execute(
                    text(query),
                    {"doc_id": document_id, "status": status}
                )
                session.commit()
                
                logger.info(f"Đã cập nhật status document {document_id} thành '{status}'")
                return True
                
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật document status: {str(e)}")
            return False
    
    def check_user_exists(self, user_id: int) -> bool:
        """
        Kiểm tra user có tồn tại không
        
        Args:
            user_id: ID của user
            
        Returns:
            True nếu user tồn tại
        """
        try:
            with self.get_session() as session:
                result = session.execute(
                    text("SELECT COUNT(*) FROM users WHERE id = :user_id"),
                    {"user_id": user_id}
                ).scalar()
                
                return result > 0
                
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra user: {str(e)}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về connection
        
        Returns:
            Connection info
        """
        try:
            if not self.engine:
                return {"status": "not_initialized"}
            
            # Get pool status
            pool = self.engine.pool
            
            return {
                "status": "connected",
                "database": settings.mysql_database,
                "host": settings.mysql_host,
                "pool_size": pool.size(),
                "checked_out_connections": pool.checked_out(),
                "overflow": pool.overflow(),
                "total": pool.size() + pool.overflow()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
mysql_client = MySQLClient()


def test_connection() -> bool:
    """Test MySQL connection"""
    try:
        if mysql_client.engine:
            with mysql_client.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
    except:
        pass
    return False


def get_mysql_client() -> MySQLClient:
    """Get MySQL client instance cho dependency injection"""
    if not mysql_client.engine:
        mysql_client.initialize()
    return mysql_client