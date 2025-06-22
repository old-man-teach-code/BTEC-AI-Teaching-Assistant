from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.document import Document
from schemas.document import DocumentCreate, DocumentUpdate
from typing import List, Optional


def create_document(db: Session, document_data: dict, owner_id: int) -> Document:
    """
    Tạo document mới trong database
    
    Args:
        db: Database session
        document_data: Dữ liệu document cần tạo
        owner_id: ID của user sở hữu document
        
    Returns:
        Document: Document đã được tạo
    """
    # Tạo đối tượng Document từ dữ liệu và gắn owner_id
    db_document = Document(**document_data, owner_id=owner_id)
    
    # Thêm vào database và commit
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Lấy document theo ID
    
    Args:
        db: Database session
        document_id: ID của document cần lấy
        
    Returns:
        Document hoặc None nếu không tìm thấy
    """
    return db.query(Document).filter(Document.id == document_id).first()


def get_document_by_filename(db: Session, filename: str) -> Optional[Document]:
    """
    Lấy document theo tên file
    
    Args:
        db: Database session
        filename: Tên file cần tìm
        
    Returns:
        Document hoặc None nếu không tìm thấy
    """
    return db.query(Document).filter(Document.filename == filename).first()


def get_user_documents(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Document]:
    """
    Lấy danh sách documents của một user, có phân trang
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu
        skip: Số documents bỏ qua (phân trang)
        limit: Số documents tối đa trả về
        
    Returns:
        Danh sách các document của user
    """
    return db.query(Document)\
        .filter(Document.owner_id == owner_id)\
        .order_by(desc(Document.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_total_user_documents(db: Session, owner_id: int) -> int:
    """
    Đếm tổng số documents của một user
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu
        
    Returns:
        Số lượng documents
    """
    return db.query(Document).filter(Document.owner_id == owner_id).count()


def update_document(
    db: Session, 
    document: Document, 
    document_update: DocumentUpdate
) -> Document:
    """
    Cập nhật thông tin document
    
    Args:
        db: Database session
        document: Document cần cập nhật
        document_update: Dữ liệu cập nhật
        
    Returns:
        Document đã được cập nhật
    """
    # Lấy dữ liệu cập nhật dưới dạng dict, loại bỏ các giá trị None
    update_data = document_update.dict(exclude_unset=True)
    
    # Cập nhật từng trường có trong update_data
    for key, value in update_data.items():
        setattr(document, key, value)
    
    # Commit thay đổi vào database
    db.commit()
    db.refresh(document)
    
    return document


def delete_document(db: Session, document: Document) -> None:
    """
    Xóa document khỏi database
    
    Args:
        db: Database session
        document: Document cần xóa
    """
    db.delete(document)
    db.commit()


def soft_delete_document(db: Session, document: Document) -> Document:
    """
    Soft delete document bằng cách cập nhật trạng thái
    
    Args:
        db: Database session
        document: Document cần xóa mềm
        
    Returns:
        Document sau khi cập nhật trạng thái
    """
    # Cập nhật trạng thái thành 'deleted' hoặc tương tự
    document.status = "deleted"
    db.commit()
    db.refresh(document)
    
    return document 