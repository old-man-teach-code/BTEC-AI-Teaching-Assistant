from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.folder import Folder
from models.document import Document
from schemas.folder import (
    FolderCreate, FolderUpdate, FolderResponse, FolderListResponse,
    FolderTreeResponse, FolderTreeNode, FolderMove
)
from crud.folder import (
    create_folder, get_active_folder, get_user_folders, get_total_user_folders,
    update_folder, soft_delete_folder, restore_folder, delete_folder,
    get_folder_with_counts, get_expired_folders, get_folder_tree
)
from crud.document import get_user_documents


def service_create_folder(
    db: Session,
    folder_data: FolderCreate,
    owner_id: int
) -> Dict[str, Any]:
    """
    Tạo folder mới
    
    Args:
        db: Database session
        folder_data: Dữ liệu folder cần tạo
        owner_id: ID của user
        
    Returns:
        Dict: Thông tin folder vừa tạo
        
    Raises:
        HTTPException: Nếu parent folder không tồn tại hoặc không có quyền
    """
    try:
        # Validate parent folder nếu có
        if folder_data.parent_id:
            parent_folder = get_active_folder(db, folder_data.parent_id)
            if not parent_folder or parent_folder.owner_id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder không tồn tại hoặc bạn không có quyền truy cập"
                )
        
        # Tạo folder
        folder = create_folder(db, folder_data, owner_id)
        
        return {
            "message": f"Folder '{folder.name}' đã được tạo thành công",
            "folder": FolderResponse(
                **folder.__dict__,
                document_count=0,
                subfolder_count=0
            )
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo folder: {str(e)}"
        )


def service_get_user_folders(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None
) -> FolderListResponse:
    """
    Lấy danh sách folders của user
    
    Args:
        db: Database session
        owner_id: ID của user
        skip: Số folders bỏ qua
        limit: Số folders tối đa
        parent_id: ID của parent folder
        
    Returns:
        FolderListResponse: Danh sách folders với metadata
    """
    try:
        # Validate parent folder nếu có
        if parent_id:
            parent_folder = get_active_folder(db, parent_id)
            if not parent_folder or parent_folder.owner_id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder không tồn tại hoặc bạn không có quyền truy cập"
                )
        
        # Lấy folders
        folders = get_user_folders(db, owner_id, skip, limit, parent_id=parent_id)
        total = get_total_user_folders(db, owner_id, parent_id=parent_id)
        
        # Tạo response với counts
        folder_responses = []
        for folder in folders:
            folder_data = get_folder_with_counts(db, folder.id, owner_id)
            if folder_data:
                folder_responses.append(FolderResponse(
                    **folder.__dict__,
                    document_count=folder_data["document_count"],
                    subfolder_count=folder_data["subfolder_count"]
                ))
        
        return FolderListResponse(
            total=total,
            items=folder_responses
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy danh sách folders: {str(e)}"
        )


def service_get_folder_tree(
    db: Session,
    owner_id: int
) -> FolderTreeResponse:
    """
    Lấy cây thư mục của user
    
    Args:
        db: Database session
        owner_id: ID của user
        
    Returns:
        FolderTreeResponse: Cây thư mục
    """
    try:
        def build_tree_node(folder: Folder) -> FolderTreeNode:
            """Xây dựng node cho cây thư mục"""
            # Lấy counts
            folder_data = get_folder_with_counts(db, folder.id, owner_id)
            document_count = folder_data["document_count"] if folder_data else 0
            subfolder_count = folder_data["subfolder_count"] if folder_data else 0
            
            # Lấy children
            children_folders = get_folder_tree(db, owner_id, folder.id)
            children = [build_tree_node(child) for child in children_folders]
            
            return FolderTreeNode(
                id=folder.id,
                name=folder.name,
                description=folder.description,
                parent_id=folder.parent_id,
                document_count=document_count,
                subfolder_count=subfolder_count,
                children=children,
                created_at=folder.created_at
            )
        
        # Lấy root folders
        root_folders = get_folder_tree(db, owner_id, None)
        tree = [build_tree_node(folder) for folder in root_folders]
        
        # Tính tổng số folders
        total = get_total_user_folders(db, owner_id)
        
        return FolderTreeResponse(
            total=total,
            tree=tree
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy cây thư mục: {str(e)}"
        )


def service_get_folder_details(
    db: Session,
    folder_id: int,
    owner_id: int
) -> FolderResponse:
    """
    Lấy chi tiết folder
    
    Args:
        db: Database session
        folder_id: ID của folder
        owner_id: ID của user
        
    Returns:
        FolderResponse: Chi tiết folder
        
    Raises:
        HTTPException: Nếu folder không tồn tại hoặc không có quyền
    """
    try:
        folder_data = get_folder_with_counts(db, folder_id, owner_id)
        if not folder_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder không tồn tại hoặc bạn không có quyền truy cập"
            )
        
        folder = folder_data["folder"]
        return FolderResponse(
            **folder.__dict__,
            document_count=folder_data["document_count"],
            subfolder_count=folder_data["subfolder_count"]
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy chi tiết folder: {str(e)}"
        )


def service_update_folder(
    db: Session,
    folder_id: int,
    folder_update: FolderUpdate,
    owner_id: int
) -> Dict[str, Any]:
    """
    Cập nhật folder
    
    Args:
        db: Database session
        folder_id: ID của folder
        folder_update: Dữ liệu cập nhật
        owner_id: ID của user
        
    Returns:
        Dict: Kết quả cập nhật
        
    Raises:
        HTTPException: Nếu folder không tồn tại hoặc không có quyền
    """
    try:
        # Validate folder access
        folder = get_active_folder(db, folder_id)
        if not folder or folder.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder không tồn tại hoặc bạn không có quyền truy cập"
            )
        
        # Validate parent folder nếu có
        if folder_update.parent_id is not None:
            if folder_update.parent_id == folder_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Folder không thể là parent của chính nó"
                )
            
            if folder_update.parent_id != 0:  # 0 means root level
                parent_folder = get_active_folder(db, folder_update.parent_id)
                if not parent_folder or parent_folder.owner_id != owner_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Parent folder không tồn tại hoặc bạn không có quyền truy cập"
                    )
        
        # Cập nhật folder
        old_name = folder.name
        updated_folder = update_folder(db, folder, folder_update)
        
        return {
            "message": f"Folder '{old_name}' đã được cập nhật thành '{updated_folder.name}'",
            "folder": FolderResponse(**updated_folder.__dict__, document_count=0, subfolder_count=0)
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật folder: {str(e)}"
        )


def service_delete_folder(
    db: Session,
    folder_id: int,
    owner_id: int,
    hard_delete: bool = False
) -> Dict[str, Any]:
    """
    Xóa folder (soft hoặc hard delete)

    Args:
        db: Database session
        folder_id: ID của folder
        owner_id: ID của user
        hard_delete: True = xóa cứng, False = xóa mềm

    Returns:
        Dict: Kết quả xóa

    Raises:
        HTTPException: Nếu folder không tồn tại hoặc không có quyền
    """
    try:
        # Validate folder access
        folder = get_active_folder(db, folder_id)
        if not folder or folder.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder không tồn tại hoặc bạn không có quyền truy cập"
            )

        if hard_delete:
            # Hard delete - xóa vĩnh viễn
            # Trước tiên cần xóa tất cả documents trong folder
            documents = db.query(Document).filter(Document.folder_id == folder_id).all()
            for doc in documents:
                db.delete(doc)

            # Xóa folder
            delete_folder(db, folder)

            return {
                "message": f"Folder '{folder.name}' đã được xóa vĩnh viễn",
                "folder_id": folder_id,
                "deleted_at": datetime.utcnow().isoformat(),
                "type": "hard_delete"
            }
        else:
            # Soft delete - chuyển vào trash
            deleted_folder = soft_delete_folder(db, folder)

            # Soft delete tất cả documents trong folder
            documents = db.query(Document).filter(
                Document.folder_id == folder_id,
                Document.is_deleted == False
            ).all()

            for doc in documents:
                doc.is_deleted = True
                doc.deleted_at = datetime.utcnow()

            db.commit()

            return {
                "message": f"Folder '{folder.name}' đã được chuyển vào trash",
                "folder_id": folder_id,
                "deleted_at": deleted_folder.deleted_at.isoformat(),
                "type": "soft_delete",
                "documents_affected": len(documents)
            }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể xóa folder: {str(e)}"
        )


def service_restore_folder(
    db: Session,
    folder_id: int,
    owner_id: int
) -> Dict[str, Any]:
    """
    Khôi phục folder từ trash

    Args:
        db: Database session
        folder_id: ID của folder
        owner_id: ID của user

    Returns:
        Dict: Kết quả khôi phục

    Raises:
        HTTPException: Nếu folder không tồn tại hoặc không có quyền
    """
    try:
        # Lấy folder (bao gồm cả deleted)
        folder = db.query(Folder).filter(
            Folder.id == folder_id,
            Folder.owner_id == owner_id,
            Folder.is_deleted == True
        ).first()

        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder không tồn tại trong trash hoặc bạn không có quyền truy cập"
            )

        # Khôi phục folder
        restored_folder = restore_folder(db, folder)

        # Khôi phục tất cả documents trong folder
        documents = db.query(Document).filter(
            Document.folder_id == folder_id,
            Document.is_deleted == True
        ).all()

        for doc in documents:
            doc.is_deleted = False
            doc.deleted_at = None

        db.commit()

        return {
            "message": f"Folder '{folder.name}' đã được khôi phục từ trash",
            "folder_id": folder_id,
            "restored_at": datetime.utcnow().isoformat(),
            "documents_restored": len(documents)
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể khôi phục folder: {str(e)}"
        )


def service_move_folder(
    db: Session,
    folder_id: int,
    move_data: FolderMove,
    owner_id: int
) -> Dict[str, Any]:
    """
    Di chuyển folder vào parent folder khác

    Args:
        db: Database session
        folder_id: ID của folder cần di chuyển
        move_data: Thông tin di chuyển
        owner_id: ID của user

    Returns:
        Dict: Kết quả di chuyển

    Raises:
        HTTPException: Nếu folder không tồn tại hoặc không có quyền
    """
    try:
        # Validate folder access
        folder = get_active_folder(db, folder_id)
        if not folder or folder.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder không tồn tại hoặc bạn không có quyền truy cập"
            )

        # Validate new parent folder
        new_parent_id = move_data.new_parent_id
        if new_parent_id == folder_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder không thể di chuyển vào chính nó"
            )

        if new_parent_id:
            new_parent = get_active_folder(db, new_parent_id)
            if not new_parent or new_parent.owner_id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder đích không tồn tại hoặc bạn không có quyền truy cập"
                )

        # Di chuyển folder
        old_parent_id = folder.parent_id
        folder.parent_id = new_parent_id
        db.commit()
        db.refresh(folder)

        # Tạo message
        if new_parent_id:
            new_parent = get_active_folder(db, new_parent_id)
            target_name = new_parent.name
        else:
            target_name = "Root"

        return {
            "message": f"Folder '{folder.name}' đã được di chuyển vào '{target_name}'",
            "folder_id": folder_id,
            "old_parent_id": old_parent_id,
            "new_parent_id": new_parent_id,
            "moved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể di chuyển folder: {str(e)}"
        )


def service_cleanup_expired_folders(
    db: Session,
    days: int = 30
) -> Dict[str, Any]:
    """
    Tự động xóa cứng các folders đã hết hạn trong trash

    Args:
        db: Database session
        days: Số ngày hết hạn

    Returns:
        Dict: Kết quả cleanup
    """
    try:
        expired_folders = get_expired_folders(db, days)

        deleted_count = 0
        for folder in expired_folders:
            # Xóa tất cả documents trong folder trước
            documents = db.query(Document).filter(Document.folder_id == folder.id).all()
            for doc in documents:
                db.delete(doc)

            # Xóa folder
            db.delete(folder)
            deleted_count += 1

        db.commit()

        return {
            "message": f"Đã xóa {deleted_count} folders hết hạn",
            "deleted_count": deleted_count,
            "expiry_days": days,
            "cleanup_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cleanup folders: {str(e)}"
        )
