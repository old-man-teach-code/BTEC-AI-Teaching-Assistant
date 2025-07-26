from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os

from models.document import Document
from models.folder import Folder
from schemas.trash import (
    BulkHardDeleteRequest, BulkHardDeleteResponse, 
    DeletedItemInfo, FailedItemInfo, TrashItemIdentifier
)
from crud.document import get_trash_document_by_id, bulk_hard_delete_documents
from crud.folder import get_trash_folder_by_id, bulk_hard_delete_folders


def service_bulk_hard_delete_trash_items(
    db: Session,
    owner_id: int,
    delete_request: BulkHardDeleteRequest
) -> BulkHardDeleteResponse:
    """
    Xóa cứng nhiều items từ trash (documents và folders)
    
    Args:
        db: Database session
        owner_id: ID của user
        delete_request: Request chứa danh sách items cần xóa
        
    Returns:
        BulkHardDeleteResponse: Kết quả xóa bulk
        
    Raises:
        HTTPException: Nếu có lỗi trong quá trình xử lý
    """
    try:
        # Khởi tạo danh sách kết quả
        deleted_items: List[DeletedItemInfo] = []
        failed_items: List[FailedItemInfo] = []
        
        # Phân loại items theo type
        documents_to_delete: List[Document] = []
        folders_to_delete: List[Folder] = []
        
        # Validate và phân loại từng item
        for item in delete_request.items:
            if item.type == "document":
                document = get_trash_document_by_id(db, item.id, owner_id)
                if document:
                    documents_to_delete.append(document)
                else:
                    failed_items.append(FailedItemInfo(
                        id=item.id,
                        type=item.type,
                        reason="Document không tồn tại trong trash hoặc bạn không có quyền truy cập"
                    ))
                    
            elif item.type == "folder":
                folder = get_trash_folder_by_id(db, item.id, owner_id)
                if folder:
                    folders_to_delete.append(folder)
                else:
                    failed_items.append(FailedItemInfo(
                        id=item.id,
                        type=item.type,
                        reason="Folder không tồn tại trong trash hoặc bạn không có quyền truy cập"
                    ))
            else:
                failed_items.append(FailedItemInfo(
                    id=item.id,
                    type=item.type,
                    reason=f"Loại item không hợp lệ: {item.type}. Chỉ hỗ trợ 'document' và 'folder'"
                ))
        
        # Thực hiện xóa documents
        for document in documents_to_delete:
            try:
                # Xóa file vật lý nếu tồn tại
                if hasattr(document, 'file_path') and document.file_path and os.path.exists(document.file_path):
                    os.remove(document.file_path)
                
                # Thêm vào danh sách đã xóa trước khi xóa khỏi DB
                deleted_items.append(DeletedItemInfo(
                    id=document.id,
                    type="document",
                    name=document.original_name,
                    deleted_at=document.deleted_at or datetime.utcnow()
                ))
                
            except Exception as e:
                failed_items.append(FailedItemInfo(
                    id=document.id,
                    type="document",
                    reason=f"Lỗi khi xóa file vật lý: {str(e)}"
                ))
                # Loại bỏ khỏi danh sách xóa
                documents_to_delete.remove(document)
        
        # Thực hiện xóa folders
        for folder in folders_to_delete:
            try:
                deleted_items.append(DeletedItemInfo(
                    id=folder.id,
                    type="folder",
                    name=folder.name,
                    deleted_at=folder.deleted_at or datetime.utcnow()
                ))
            except Exception as e:
                failed_items.append(FailedItemInfo(
                    id=folder.id,
                    type="folder",
                    reason=f"Lỗi khi chuẩn bị xóa folder: {str(e)}"
                ))
                # Loại bỏ khỏi danh sách xóa
                folders_to_delete.remove(folder)
        
        # Thực hiện xóa cứng từ database
        documents_deleted = bulk_hard_delete_documents(db, documents_to_delete) if documents_to_delete else 0
        folders_deleted = bulk_hard_delete_folders(db, folders_to_delete) if folders_to_delete else 0
        
        total_successfully_deleted = documents_deleted + folders_deleted
        total_failed = len(failed_items)
        total_requested = len(delete_request.items)
        
        # Tạo response message
        if total_successfully_deleted == total_requested:
            message = f"Đã xóa vĩnh viễn tất cả {total_successfully_deleted} items từ trash"
        elif total_successfully_deleted > 0:
            message = f"Đã xóa vĩnh viễn {total_successfully_deleted}/{total_requested} items từ trash"
        else:
            message = "Không có item nào được xóa"
        
        return BulkHardDeleteResponse(
            message=message,
            total_requested=total_requested,
            successfully_deleted=total_successfully_deleted,
            failed_to_delete=total_failed,
            deleted_items=deleted_items,
            failed_items=failed_items,
            operation_completed_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể thực hiện xóa cứng bulk: {str(e)}"
        )
