from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from cache.redis_client import get_cache, set_cache
from datetime import datetime
import time
from services.file_service import validate_file

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
