from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from models.folder import Folder
from models.document import Document
from schemas.folder import FolderContentResponse, FolderContentItem, FolderResponse
from crud.folder import get_active_folder, get_user_folders, get_folder_with_counts
from crud.document import get_user_documents
from sqlalchemy import or_, func


def _format_file_size(size_bytes: int) -> str:
    """
    Format file size thành string dễ đọc
    
    Args:
        size_bytes: Kích thước file tính bằng bytes
        
    Returns:
        str: Kích thước file đã format (B, KB, MB, GB)
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_bytes = float(size_bytes)
    size_index = 0
    
    while size_bytes >= 1024 and size_index < len(size_names) - 1:
        size_bytes /= 1024
        size_index += 1
    
    if size_index == 0:
        return f"{int(size_bytes)} {size_names[size_index]}"
    else:
        return f"{size_bytes:.1f} {size_names[size_index]}"


def _get_file_extension(filename: str) -> str:
    """
    Lấy extension của file
    
    Args:
        filename: Tên file
        
    Returns:
        str: Extension (không bao gồm dấu chấm)
    """
    if not filename:
        return ""
    
    ext = os.path.splitext(filename)[1]
    return ext.lower().lstrip('.') if ext else ""


def _get_file_type_from_extension(extension: str) -> str:
    """
    Xác định loại file từ extension
    
    Args:
        extension: File extension
        
    Returns:
        str: Loại file (PDF, DOCX, PPTX, etc.)
    """
    extension = extension.lower()
    
    type_mapping = {
        'pdf': 'PDF',
        'doc': 'DOCX',
        'docx': 'DOCX', 
        'ppt': 'PPTX',
        'pptx': 'PPTX',
        'xls': 'XLSX',
        'xlsx': 'XLSX',
        'csv': 'CSV',
        'txt': 'TXT',
        'jpg': 'IMAGE',
        'jpeg': 'IMAGE',
        'png': 'IMAGE',
        'gif': 'IMAGE',
        'bmp': 'IMAGE',
        'svg': 'IMAGE',
    }
    
    return type_mapping.get(extension, extension.upper() if extension else 'UNKNOWN')


def _calculate_folder_total_size(db: Session, folder_id: int, owner_id: int) -> int:
    """
    Tính tổng kích thước của tất cả files trong folder (bao gồm subfolders)
    
    Args:
        db: Database session
        folder_id: ID của folder
        owner_id: ID của user
        
    Returns:
        int: Tổng kích thước tính bằng bytes
    """
    try:
        # Lấy tổng size của documents trực tiếp trong folder
        direct_size = db.query(func.sum(Document.file_size)).filter(
            Document.folder_id == folder_id,
            Document.owner_id == owner_id,
            Document.is_deleted == False
        ).scalar() or 0
        
        print(f"[DEBUG] Folder {folder_id} direct size: {direct_size}")
        
        # Lấy tổng size của các subfolders
        subfolders = db.query(Folder).filter(
            Folder.parent_id == folder_id,
            Folder.owner_id == owner_id,
            Folder.is_deleted == False
        ).all()
        
        print(f"[DEBUG] Folder {folder_id} has {len(subfolders)} subfolders")
        
        subfolder_size = 0
        for subfolder in subfolders:
            subfolder_size += _calculate_folder_total_size(db, subfolder.id, owner_id)
        
        total_size = direct_size + subfolder_size
        print(f"[DEBUG] Folder {folder_id} total size: {total_size}")
        
        return total_size
        
    except Exception as e:
        print(f"Error calculating folder size: {e}")
        return 0


def _apply_sorting(items: List[FolderContentItem], sort_by: str) -> List[FolderContentItem]:
    """
    Áp dụng sorting cho danh sách items
    
    Args:
        items: Danh sách items cần sort
        sort_by: Loại sorting
        
    Returns:
        List[FolderContentItem]: Danh sách đã được sort
    """
    if sort_by == "name_asc":
        return sorted(items, key=lambda x: x.name.lower())
    elif sort_by == "name_desc":
        return sorted(items, key=lambda x: x.name.lower(), reverse=True)
    elif sort_by == "size_asc":
        return sorted(items, key=lambda x: (x.size or x.total_size or 0))
    elif sort_by == "size_desc":
        return sorted(items, key=lambda x: (x.size or x.total_size or 0), reverse=True)
    elif sort_by == "date_asc":
        return sorted(items, key=lambda x: x.created_at)
    elif sort_by == "date_desc":
        return sorted(items, key=lambda x: x.created_at, reverse=True)
    elif sort_by == "type_asc":
        return sorted(items, key=lambda x: (x.type, x.name.lower()))
    elif sort_by == "type_desc":
        return sorted(items, key=lambda x: (x.type, x.name.lower()), reverse=True)
    else:
        # Default: sort by date desc
        return sorted(items, key=lambda x: x.created_at, reverse=True)


def _apply_filtering(items: List[FolderContentItem], filter_by: str) -> List[FolderContentItem]:
    """
    Áp dụng filtering cho danh sách items
    
    Args:
        items: Danh sách items cần filter
        filter_by: Loại filter
        
    Returns:
        List[FolderContentItem]: Danh sách đã được filter
    """
    if filter_by == "all":
        return items
    elif filter_by == "folder":
        return [item for item in items if item.type == "folder"]
    else:
        # Filter theo file type (pdf, docx, pptx, etc.)
        target_type = filter_by.upper()
        return [item for item in items if item.type == "document" and (item.file_type == target_type or item.extension == filter_by.lower())]


def _apply_search(items: List[FolderContentItem], search: str) -> List[FolderContentItem]:
    """
    Áp dụng tìm kiếm cho danh sách items
    
    Args:
        items: Danh sách items cần tìm kiếm
        search: Từ khóa tìm kiếm
        
    Returns:
        List[FolderContentItem]: Danh sách đã được filter theo search
    """
    if not search or not search.strip():
        return items
    
    search_lower = search.strip().lower()
    return [item for item in items if search_lower in item.name.lower()]


def service_get_folder_contents(
    db: Session,
    owner_id: int,
    folder_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "date_desc",
    filter_by: str = "all",
    search: Optional[str] = None
) -> FolderContentResponse:
    """
    Lấy nội dung folder với sorting, filtering và pagination
    
    Args:
        db: Database session
        owner_id: ID của user
        folder_id: ID của folder (None = root level)
        skip: Số items bỏ qua (pagination)
        limit: Số items tối đa
        sort_by: Loại sorting
        filter_by: Loại filtering
        search: Từ khóa tìm kiếm
        
    Returns:
        FolderContentResponse: Nội dung folder với metadata
    """
    try:
        # Validate folder nếu có
        folder_info = None
        if folder_id:
            folder = get_active_folder(db, folder_id)
            if not folder or folder.owner_id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder không tồn tại hoặc bạn không có quyền truy cập"
                )
            
            # Lấy thông tin folder với counts
            folder_data = get_folder_with_counts(db, folder_id, owner_id)
            if folder_data:
                folder_info = FolderResponse(
                    **folder.__dict__,
                    document_count=folder_data["document_count"],
                    subfolder_count=folder_data["subfolder_count"]
                )
        
        # Lấy danh sách subfolders
        folders = get_user_folders(db, owner_id, 0, 10000, parent_id=folder_id)  # Lấy tất cả folders
        
        # Lấy danh sách documents trong folder
        documents = get_user_documents(db, owner_id, 0, 10000, folder_id=folder_id)  # Lấy tất cả documents
        
        # Tạo danh sách items
        items = []
        
        # Thêm folders vào danh sách
        for folder in folders:
            folder_data = get_folder_with_counts(db, folder.id, owner_id)
            total_size = _calculate_folder_total_size(db, folder.id, owner_id)
            
            print(f"[DEBUG] Creating FolderContentItem for '{folder.name}' (ID: {folder.id})")
            print(f"[DEBUG] - total_size: {total_size}")
            print(f"[DEBUG] - formatted: {_format_file_size(total_size) if total_size > 0 else '0 B'}")
            
            items.append(FolderContentItem(
                id=folder.id,
                name=folder.name,
                type="folder",
                size=None,
                size_formatted=None,
                file_type=None,
                extension=None,
                document_count=folder_data["document_count"] if folder_data else 0,
                subfolder_count=folder_data["subfolder_count"] if folder_data else 0,
                total_size=total_size,
                total_size_formatted=_format_file_size(total_size) if total_size > 0 else "0 B",
                created_at=folder.created_at,
                updated_at=folder.updated_at
            ))
        
        # Thêm documents vào danh sách
        for doc in documents:
            extension = _get_file_extension(doc.original_name or doc.filename)
            file_type = _get_file_type_from_extension(extension) if extension else "UNKNOWN"
            
            items.append(FolderContentItem(
                id=doc.id,
                name=doc.original_name or doc.filename,
                type="document",
                size=doc.file_size,
                size_formatted=_format_file_size(doc.file_size) if doc.file_size else "0 B",
                file_type=file_type,
                extension=extension,
                document_count=None,
                subfolder_count=None,
                total_size=None,
                total_size_formatted=None,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ))
        
        # Áp dụng tìm kiếm
        if search:
            items = _apply_search(items, search)
        
        # Áp dụng filtering
        items = _apply_filtering(items, filter_by)
        
        # Lưu tổng số items trước khi áp dụng sorting và pagination
        total_items = len(items)
        
        # Áp dụng sorting
        items = _apply_sorting(items, sort_by)
        
        # Áp dụng pagination
        paginated_items = items[skip:skip + limit]
        
        return FolderContentResponse(
            total=total_items,
            items=paginated_items,
            folder_info=folder_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy nội dung folder: {str(e)}"
        )