from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from models.document import Document, DocumentStatus
from schemas.document import DocumentCreate, DocumentUpdate
from typing import List, Optional
from datetime import datetime, timedelta


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
    Lấy document theo ID (bao gồm cả deleted documents)

    Args:
        db: Database session
        document_id: ID của document cần lấy

    Returns:
        Document hoặc None nếu không tìm thấy
    """
    return db.query(Document).filter(Document.id == document_id).first()


def get_active_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Lấy document theo ID (chỉ active documents)

    Args:
        db: Database session
        document_id: ID của document cần lấy

    Returns:
        Document hoặc None nếu không tìm thấy hoặc đã bị xóa
    """
    return db.query(Document).filter(
        and_(Document.id == document_id, Document.is_deleted == False)
    ).first()


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
    limit: int = 100,
    include_deleted: bool = False,
    folder_id: Optional[int] = None
) -> List[Document]:
    """
    Lấy danh sách documents của một user, có phân trang

    Args:
        db: Database session
        owner_id: ID của user sở hữu
        skip: Số documents bỏ qua (phân trang)
        limit: Số documents tối đa trả về
        include_deleted: Có bao gồm deleted documents không
        folder_id: Lọc theo folder (None = root level, "all" = tất cả)

    Returns:
        Danh sách các document của user
    """
    # Query cơ bản
    query = db.query(Document).filter(Document.owner_id == owner_id)

    # Filter deleted documents
    if not include_deleted:
        query = query.filter(Document.is_deleted == False)

    # Filter by folder_id
    if folder_id is not None:
        query = query.filter(Document.folder_id == folder_id)
    elif folder_id != "all":  # Nếu không phải "all", lọc root level
        query = query.filter(Document.folder_id.is_(None))

    return query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()


def get_total_user_documents(
    db: Session,
    owner_id: int,
    include_deleted: bool = False,
    folder_id: Optional[int] = None
) -> int:
    """
    Đếm tổng số documents của một user

    Args:
        db: Database session
        owner_id: ID của user sở hữu
        include_deleted: Có bao gồm deleted documents không
        folder_id: Lọc theo folder

    Returns:
        Số lượng documents
    """
    # Query cơ bản
    query = db.query(Document).filter(Document.owner_id == owner_id)

    # Filter deleted documents
    if not include_deleted:
        query = query.filter(Document.is_deleted == False)

    # Filter by folder_id
    if folder_id is not None:
        query = query.filter(Document.folder_id == folder_id)
    elif folder_id != "all":
        query = query.filter(Document.folder_id.is_(None))

    return query.count()


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
    # Cập nhật trạng thái và đánh dấu deleted
    document.status = DocumentStatus.DELETED.value
    document.is_deleted = True
    document.deleted_at = datetime.utcnow()

    db.commit()
    db.refresh(document)

    return document


def restore_document(db: Session, document: Document, folder_id: Optional[int] = None) -> Document:
    """
    Khôi phục document từ trash

    Args:
        db: Database session
        document: Document cần khôi phục
        folder_id: Folder đích khi khôi phục (None = root level)

    Returns:
        Document sau khi khôi phục
    """
    # Khôi phục trạng thái
    document.status = DocumentStatus.READY.value  # Hoặc trạng thái phù hợp
    document.is_deleted = False
    document.deleted_at = None

    # Đặt folder_id nếu được chỉ định
    if folder_id is not None:
        document.folder_id = folder_id

    db.commit()
    db.refresh(document)

    return document


def get_user_trash_documents(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Document]:
    """
    Lấy danh sách documents trong trash của user

    Args:
        db: Database session
        owner_id: ID của user sở hữu
        skip: Số documents bỏ qua (phân trang)
        limit: Số documents tối đa trả về

    Returns:
        Danh sách documents trong trash
    """
    return db.query(Document).filter(
        and_(
            Document.owner_id == owner_id,
            Document.is_deleted == True
        )
    ).order_by(desc(Document.deleted_at)).offset(skip).limit(limit).all()


def get_total_user_trash_documents(db: Session, owner_id: int) -> int:
    """
    Đếm tổng số documents trong trash của user

    Args:
        db: Database session
        owner_id: ID của user sở hữu

    Returns:
        Số lượng documents trong trash
    """
    return db.query(Document).filter(
        and_(
            Document.owner_id == owner_id,
            Document.is_deleted == True
        )
    ).count()


def get_trash_document_by_id(db: Session, document_id: int, owner_id: int) -> Optional[Document]:
    """
    Lấy document trong trash theo ID và owner

    Args:
        db: Database session
        document_id: ID của document
        owner_id: ID của user sở hữu

    Returns:
        Optional[Document]: Document nếu tìm thấy trong trash, None nếu không
    """
    return db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.owner_id == owner_id,
            Document.is_deleted == True
        )
    ).first()


def bulk_hard_delete_documents(db: Session, documents: List[Document]) -> int:
    """
    Xóa cứng nhiều documents khỏi database

    Args:
        db: Database session
        documents: Danh sách documents cần xóa cứng

    Returns:
        int: Số lượng documents đã xóa thành công
    """
    deleted_count = 0
    for document in documents:
        try:
            db.delete(document)
            deleted_count += 1
        except Exception as e:
            print(f"Lỗi khi xóa document {document.id}: {str(e)}")
            continue

    db.commit()
    return deleted_count


def get_expired_documents(db: Session, days: int = 30) -> List[Document]:
    """
    Lấy danh sách documents đã hết hạn trong trash (để auto-cleanup)

    Args:
        db: Database session
        days: Số ngày hết hạn (mặc định 30 ngày)

    Returns:
        List[Document]: Danh sách documents hết hạn
    """
    expiry_date = datetime.utcnow() - timedelta(days=days)

    return db.query(Document).filter(
        and_(
            Document.is_deleted == True,
            Document.deleted_at <= expiry_date
        )
    ).all()


def move_document_to_folder(db: Session, document: Document, folder_id: Optional[int]) -> Document:
    """
    Di chuyển document vào folder khác

    Args:
        db: Database session
        document: Document cần di chuyển
        folder_id: ID của folder đích (None = root level)

    Returns:
        Document sau khi di chuyển
    """
    document.folder_id = folder_id
    db.commit()
    db.refresh(document)

    return document


def get_latest_user_document(db: Session, owner_id: int) -> Optional[Document]:
    """
    Lấy document mới nhất (theo created_at) của một user

    Args:
        db: Database session
        owner_id: ID của user sở hữu

    Returns:
        Document mới nhất hoặc None nếu không có document
    """
    return db.query(Document).filter(
        and_(
            Document.owner_id == owner_id,
            Document.is_deleted == False
        )
    ).order_by(desc(Document.created_at)).first()