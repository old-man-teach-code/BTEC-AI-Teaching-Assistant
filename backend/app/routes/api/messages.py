from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from schemas.message import MessageCreate, MessageRead, MessageUpdate, MessageSearch
from services.message_service import MessageService
from dependencies.deps import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Tạo message mới để lưu lại lịch sử trò chuyện.
    Cần JWT authentication.
    
    Request body:
    {
        "threadId": "thread_123",
        "content": "Nội dung tin nhắn",
        "dName": "Tên hiển thị (tuỳ chọn)"
    }
    """
    try:
        message_service = MessageService(db)
        return message_service.create_new_message(message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/", response_model=List[MessageRead])
def get_all_messages(
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of messages to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy danh sách tất cả messages với phân trang.
    Cần JWT authentication.
    """
    try:
        message_service = MessageService(db)
        return message_service.get_all_messages(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages: {str(e)}"
        )

@router.get("/thread/{thread_id}", response_model=List[MessageRead])
def get_messages_by_thread(
    thread_id: str,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of messages to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy danh sách messages theo threadId với phân trang.
    Cần JWT authentication.
    """
    try:
        message_service = MessageService(db)
        messages = message_service.get_thread_messages(thread_id, skip=skip, limit=limit)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages for thread: {str(e)}"
        )

@router.get("/{message_id}", response_model=MessageRead)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy message theo ID.
    Cần JWT authentication.
    """
    try:
        message_service = MessageService(db)
        message = message_service.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching message: {str(e)}"
        )

@router.put("/{message_id}", response_model=MessageRead)
def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Cập nhật message theo ID.
    Cần JWT authentication.
    """
    try:
        message_service = MessageService(db)
        updated_message = message_service.update_message_by_id(message_id, message_update)
        if not updated_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        return updated_message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating message: {str(e)}"
        )

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Xóa message theo ID.
    Cần JWT authentication.
    """
    try:
        message_service = MessageService(db)
        success = message_service.delete_message_by_id(message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        )

@router.get("/thread/{thread_id}/count")
def get_thread_message_count(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Đếm số lượng messages trong một thread.
    Cần JWT authentication.
    """
    try:
        message_service = MessageService(db)
        count = message_service.get_thread_message_count(thread_id)
        return {"thread_id": thread_id, "message_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting messages: {str(e)}"
        )

@router.post("/search")
def search_message(
    search_data: MessageSearch,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Tìm kiếm message theo content và dName.
    Cần JWT authentication.
    
    Request body:
    {
        "content": "bạn biết môn AD ko vậy.",
        "dName": "Pham Qui Luc"
    }
    
    Trả về toàn bộ thông tin của message nếu tìm thấy, ngược lại trả về false.
    """
    try:
        message_service = MessageService(db)
        result = message_service.search_message_by_content_and_dname(
            content=search_data.content,
            dName=search_data.dName
        )
        
        if result:
            return result
        else:
            return {"success": False, "message": "Không tìm thấy message phù hợp"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching message: {str(e)}"
        )