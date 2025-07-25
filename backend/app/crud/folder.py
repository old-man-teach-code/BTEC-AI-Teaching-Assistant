from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.folder import Folder
from models.document import Document
from schemas.folder import FolderCreate, FolderUpdate


def create_folder(db: Session, folder_data: FolderCreate, owner_id: int) -> Folder:
    """
    Tạo folder mới
    
    Args:
        db: Database session
        folder_data: Dữ liệu folder cần tạo
        owner_id: ID của user sở hữu folder
        
    Returns:
        Folder: Folder vừa được tạo
    """
    db_folder = Folder(
        name=folder_data.name,
        description=folder_data.description,
        parent_id=folder_data.parent_id,
        owner_id=owner_id
    )
    
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    
    return db_folder


def get_folder(db: Session, folder_id: int) -> Optional[Folder]:
    """
    Lấy folder theo ID
    
    Args:
        db: Database session
        folder_id: ID của folder
        
    Returns:
        Optional[Folder]: Folder nếu tìm thấy, None nếu không
    """
    return db.query(Folder).filter(Folder.id == folder_id).first()


def get_active_folder(db: Session, folder_id: int) -> Optional[Folder]:
    """
    Lấy folder chưa bị xóa theo ID
    
    Args:
        db: Database session
        folder_id: ID của folder
        
    Returns:
        Optional[Folder]: Folder nếu tìm thấy và chưa bị xóa, None nếu không
    """
    return db.query(Folder).filter(
        and_(
            Folder.id == folder_id,
            Folder.is_deleted == False
        )
    ).first()


def get_user_folders(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100,
    include_deleted: bool = False,
    parent_id: Optional[int] = None
) -> List[Folder]:
    """
    Lấy danh sách folders của một user
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu folders
        skip: Số folders bỏ qua (phân trang)
        limit: Số folders tối đa trả về
        include_deleted: Có bao gồm deleted folders không
        parent_id: Lọc theo parent folder (None = root level)
        
    Returns:
        Danh sách các folder của user
    """
    # Query cơ bản
    query = db.query(Folder).filter(Folder.owner_id == owner_id)
    
    # Filter deleted folders
    if not include_deleted:
        query = query.filter(Folder.is_deleted == False)
    
    # Filter by parent_id
    if parent_id is not None:
        query = query.filter(Folder.parent_id == parent_id)
    else:
        query = query.filter(Folder.parent_id.is_(None))
    
    return query.offset(skip).limit(limit).all()


def get_total_user_folders(
    db: Session, 
    owner_id: int,
    include_deleted: bool = False,
    parent_id: Optional[int] = None
) -> int:
    """
    Đếm tổng số folders của một user
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu folders
        include_deleted: Có bao gồm deleted folders không
        parent_id: Lọc theo parent folder
        
    Returns:
        Số lượng folders
    """
    # Query cơ bản
    query = db.query(Folder).filter(Folder.owner_id == owner_id)
    
    # Filter deleted folders
    if not include_deleted:
        query = query.filter(Folder.is_deleted == False)
    
    # Filter by parent_id
    if parent_id is not None:
        query = query.filter(Folder.parent_id == parent_id)
    else:
        query = query.filter(Folder.parent_id.is_(None))
    
    return query.count()


def update_folder(db: Session, folder: Folder, folder_update: FolderUpdate) -> Folder:
    """
    Cập nhật thông tin folder
    
    Args:
        db: Database session
        folder: Folder cần cập nhật
        folder_update: Dữ liệu cập nhật
        
    Returns:
        Folder sau khi cập nhật
    """
    update_data = folder_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(folder, field, value)
    
    db.commit()
    db.refresh(folder)
    
    return folder


def soft_delete_folder(db: Session, folder: Folder) -> Folder:
    """
    Xóa mềm folder (đánh dấu là deleted)
    
    Args:
        db: Database session
        folder: Folder cần xóa mềm
        
    Returns:
        Folder sau khi xóa mềm
    """
    folder.is_deleted = True
    folder.deleted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(folder)
    
    return folder


def restore_folder(db: Session, folder: Folder) -> Folder:
    """
    Khôi phục folder từ trash
    
    Args:
        db: Database session
        folder: Folder cần khôi phục
        
    Returns:
        Folder sau khi khôi phục
    """
    folder.is_deleted = False
    folder.deleted_at = None
    
    db.commit()
    db.refresh(folder)
    
    return folder


def delete_folder(db: Session, folder: Folder) -> None:
    """
    Xóa cứng folder khỏi database
    
    Args:
        db: Database session
        folder: Folder cần xóa
    """
    db.delete(folder)
    db.commit()


def get_folder_with_counts(db: Session, folder_id: int, owner_id: int) -> Optional[Dict[str, Any]]:
    """
    Lấy folder kèm theo số lượng documents và subfolders
    
    Args:
        db: Database session
        folder_id: ID của folder
        owner_id: ID của user (để kiểm tra quyền)
        
    Returns:
        Dict chứa folder và counts, None nếu không tìm thấy
    """
    # Lấy folder
    folder = db.query(Folder).filter(
        and_(
            Folder.id == folder_id,
            Folder.owner_id == owner_id,
            Folder.is_deleted == False
        )
    ).first()
    
    if not folder:
        return None
    
    # Đếm documents
    document_count = db.query(Document).filter(
        and_(
            Document.folder_id == folder_id,
            Document.owner_id == owner_id,
            Document.is_deleted == False
        )
    ).count()
    
    # Đếm subfolders
    subfolder_count = db.query(Folder).filter(
        and_(
            Folder.parent_id == folder_id,
            Folder.owner_id == owner_id,
            Folder.is_deleted == False
        )
    ).count()
    
    return {
        "folder": folder,
        "document_count": document_count,
        "subfolder_count": subfolder_count
    }


def get_user_trash_folders(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Folder]:
    """
    Lấy danh sách folders trong trash của user

    Args:
        db: Database session
        owner_id: ID của user sở hữu
        skip: Số folders bỏ qua (phân trang)
        limit: Số folders tối đa trả về

    Returns:
        Danh sách folders trong trash
    """
    return db.query(Folder).filter(
        and_(
            Folder.owner_id == owner_id,
            Folder.is_deleted == True
        )
    ).order_by(desc(Folder.deleted_at)).offset(skip).limit(limit).all()


def get_total_user_trash_folders(db: Session, owner_id: int) -> int:
    """
    Đếm tổng số folders trong trash của user

    Args:
        db: Database session
        owner_id: ID của user sở hữu

    Returns:
        Số lượng folders trong trash
    """
    return db.query(Folder).filter(
        and_(
            Folder.owner_id == owner_id,
            Folder.is_deleted == True
        )
    ).count()


def get_trash_folder_by_id(db: Session, folder_id: int, owner_id: int) -> Optional[Folder]:
    """
    Lấy folder trong trash theo ID và owner

    Args:
        db: Database session
        folder_id: ID của folder
        owner_id: ID của user sở hữu

    Returns:
        Optional[Folder]: Folder nếu tìm thấy trong trash, None nếu không
    """
    return db.query(Folder).filter(
        and_(
            Folder.id == folder_id,
            Folder.owner_id == owner_id,
            Folder.is_deleted == True
        )
    ).first()


def bulk_hard_delete_folders(db: Session, folders: List[Folder]) -> int:
    """
    Xóa cứng nhiều folders khỏi database (bao gồm cả documents bên trong)

    Args:
        db: Database session
        folders: Danh sách folders cần xóa cứng

    Returns:
        int: Số lượng folders đã xóa thành công
    """
    deleted_count = 0
    for folder in folders:
        try:
            # Xóa tất cả documents trong folder trước
            documents = db.query(Document).filter(Document.folder_id == folder.id).all()
            for doc in documents:
                db.delete(doc)

            # Xóa folder
            db.delete(folder)
            deleted_count += 1
        except Exception as e:
            print(f"Lỗi khi xóa folder {folder.id}: {str(e)}")
            continue

    db.commit()
    return deleted_count


def get_expired_folders(db: Session, days: int = 30) -> List[Folder]:
    """
    Lấy danh sách folders đã hết hạn trong trash (để auto-cleanup)

    Args:
        db: Database session
        days: Số ngày hết hạn (mặc định 30 ngày)

    Returns:
        List[Folder]: Danh sách folders hết hạn
    """
    expiry_date = datetime.utcnow() - timedelta(days=days)

    return db.query(Folder).filter(
        and_(
            Folder.is_deleted == True,
            Folder.deleted_at <= expiry_date
        )
    ).all()


def get_folder_tree(db: Session, owner_id: int, parent_id: Optional[int] = None) -> List[Folder]:
    """
    Lấy cây thư mục của user
    
    Args:
        db: Database session
        owner_id: ID của user
        parent_id: ID của folder cha (None = root level)
        
    Returns:
        List[Folder]: Danh sách folders theo cấu trúc cây
    """
    return db.query(Folder).filter(
        and_(
            Folder.owner_id == owner_id,
            Folder.parent_id == parent_id,
            Folder.is_deleted == False
        )
    ).order_by(Folder.name).all()
