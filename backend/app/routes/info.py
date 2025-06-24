from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from cache.redis_client import get_cache, set_cache
from datetime import datetime
import time
from services.file_service import validate_file
from services.chromadb_client import chromadb_client
from typing import Dict, List

router = APIRouter()

@router.get("/server-time")
async def get_server_time():
    """
    Lấy thời gian hiện tại của server.
    Minh họa cách sử dụng Redis cache.
    """
    # Khóa cache có thể được tạo từ thông tin xác định
    cache_key = "server_time_info"
    
    # Thử lấy kết quả từ cache trước
    cached_data = get_cache(cache_key)
    
    # Nếu có dữ liệu trong cache, sử dụng luôn
    if cached_data:
        # Thêm thông tin lấy từ cache để minh họa
        cached_data["from_cache"] = True
        return cached_data
    
    # Nếu không có trong cache, tính toán kết quả mới
    # Giả lập một tác vụ tốn thời gian (0.1 giây)
    time.sleep(0.1)
    
    # Tạo dữ liệu mới
    current_time = datetime.now()
    result = {
        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": int(current_time.timestamp()),
        "timezone": current_time.astimezone().tzname(),
        "from_cache": False
    }
    
    # Lưu vào cache với thời gian hết hạn là 30 giây
    # (thời gian đủ dài để dễ kiểm tra nhưng không quá lâu cho việc testing)
    set_cache(cache_key, result, ttl=30)
    
    return result

@router.get("/clear-cache/{key}")
async def clear_specific_cache(key: str):
    """
    Xóa một key cụ thể khỏi cache.
    Chỉ sử dụng cho mục đích debug.
    """
    from cache.redis_client import delete_cache
    success = delete_cache(key)
    return {"success": success, "message": f"Đã xóa cache key: {key}"}

@router.post("/validate-file")
async def validate_file_endpoint(file: UploadFile = File(...)):
    """
    Kiểm tra tính hợp lệ của file
    
    - **file**: File cần kiểm tra
    """
    is_valid, error_message = validate_file(file)
    
    return {
        "valid": is_valid,
        "filename": file.filename,
        "content_type": file.content_type,
        "error_message": error_message if not is_valid else None
    }

@router.get("/health")
def health_check():
    """
    Endpoint kiểm tra trạng thái hoạt động của API
    """
    return {"status": "ok"}

@router.get("/chromadb/collections")
def list_chromadb_collections() -> Dict[str, List[str]]:
    """
    Liệt kê tất cả các collections trong ChromaDB
    
    Returns:
        Dict[str, List[str]]: Danh sách tên các collections
    """
    try:
        collections = chromadb_client.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy cập ChromaDB: {str(e)}")

@router.post("/chromadb/teacher-collection/{teacher_id}")
def create_teacher_collection(teacher_id: str) -> Dict:
    """
    Tạo collection cho giảng viên
    
    Args:
        teacher_id (str): ID của giảng viên
        
    Returns:
        Dict: Thông tin về collection đã tạo
    """
    try:
        result = chromadb_client.create_teacher_collection(teacher_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo collection: {str(e)}")

@router.delete("/chromadb/teacher-collection/{teacher_id}")
def delete_teacher_collection(teacher_id: str) -> Dict:
    """
    Xóa collection của giảng viên
    
    Args:
        teacher_id (str): ID của giảng viên
        
    Returns:
        Dict: Kết quả xóa collection
    """
    try:
        success = chromadb_client.delete_teacher_collection(teacher_id)
        if success:
            return {"status": "deleted", "teacher_id": teacher_id}
        else:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy collection cho giảng viên {teacher_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa collection: {str(e)}")
