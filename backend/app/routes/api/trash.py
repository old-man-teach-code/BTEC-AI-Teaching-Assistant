from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.deps import get_db, get_current_user
from models.user import User
from schemas.trash import BulkHardDeleteRequest, BulkHardDeleteResponse
from services.trash_service import service_bulk_hard_delete_trash_items

router = APIRouter()


@router.delete("/items", response_model=BulkHardDeleteResponse)
def bulk_hard_delete_trash_items(
    delete_request: BulkHardDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa cứng (vĩnh viễn) nhiều items từ trash
    
    Endpoint này cho phép xóa vĩnh viễn các documents và folders đã được chuyển vào trash.
    Chỉ có thể xóa các items thuộc sở hữu của user hiện tại và đang ở trong trash (is_deleted=True).
    
    Args:
        delete_request: Danh sách items cần xóa cứng
        db: Database session
        current_user: User hiện tại (từ JWT token)
        
    Returns:
        BulkHardDeleteResponse: Kết quả xóa bulk với thông tin chi tiết
        
    Raises:
        HTTPException: 
            - 400: Nếu request không hợp lệ
            - 401: Nếu không có quyền truy cập
            - 500: Nếu có lỗi server
            
    Note:
        - Items sẽ được xóa vĩnh viễn và không thể khôi phục
        - Chỉ xóa được items trong trash (is_deleted=True)
        - Tối đa 100 items mỗi request
        - Khi xóa folder, tất cả documents bên trong cũng sẽ bị xóa
        - Files vật lý cũng sẽ được xóa khỏi storage
    """
    return service_bulk_hard_delete_trash_items(db, current_user.id, delete_request)
