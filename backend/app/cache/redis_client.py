import redis
import json
from typing import Any, Optional, Union
from core.config import settings

# Lấy thông tin kết nối Redis từ cấu hình
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB
REDIS_PASSWORD = settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None
DEFAULT_TTL = settings.REDIS_DEFAULT_TTL

try:
    # Tạo kết nối đến Redis server
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True  # Tự động decode bytes thành string
    )
    # Ping để kiểm tra kết nối
    redis_client.ping()
    print(f"Kết nối Redis thành công tại {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    print(f"Không thể kết nối đến Redis: {e}")
    # Tạo redis client giả lập khi không có kết nối thực
    class DummyRedis:
        def set(self, *args, **kwargs):
            print("WARNING: Sử dụng Redis giả lập, dữ liệu không được lưu trữ")
            return True

        def get(self, *args, **kwargs):
            print("WARNING: Sử dụng Redis giả lập, không có dữ liệu")
            return None

        def delete(self, *args, **kwargs):
            print("WARNING: Sử dụng Redis giả lập, không có thao tác xóa")
            return 0
            
        def flushdb(self, *args, **kwargs):
            print("WARNING: Sử dụng Redis giả lập, không có thao tác flush")
            return True

    redis_client = DummyRedis()

def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    Lưu giá trị vào Redis cache
    
    Args:
        key: Khóa để lưu trữ giá trị
        value: Giá trị cần lưu (sẽ tự động chuyển thành JSON)
        ttl: Thời gian sống của key (giây), mặc định là 1 giờ
        
    Returns:
        bool: True nếu lưu thành công, False nếu có lỗi
    """
    try:
        # Chuyển đổi giá trị thành JSON để lưu trữ
        serialized_value = json.dumps(value) if not isinstance(value, (str, int, float, bool)) else value
        return redis_client.set(key, serialized_value, ex=ttl)
    except Exception as e:
        print(f"Lỗi khi lưu vào cache: {e}")
        return False

def get_cache(key: str) -> Optional[Any]:
    """
    Lấy giá trị từ Redis cache
    
    Args:
        key: Khóa cần lấy giá trị
        
    Returns:
        Any: Giá trị của key hoặc None nếu không tìm thấy
    """
    try:
        value = redis_client.get(key)
        if value is None:
            return None
        
        # Thử parse giá trị từ JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # Nếu không phải JSON, trả về giá trị nguyên bản
            return value
    except Exception as e:
        print(f"Lỗi khi lấy từ cache: {e}")
        return None

def delete_cache(key: str) -> bool:
    """
    Xóa giá trị khỏi Redis cache
    
    Args:
        key: Khóa cần xóa
        
    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi
    """
    try:
        return bool(redis_client.delete(key))
    except Exception as e:
        print(f"Lỗi khi xóa khỏi cache: {e}")
        return False

def flush_cache() -> bool:
    """
    Xóa toàn bộ cache (chỉ sử dụng trong môi trường phát triển)
    
    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi
    """
    try:
        return redis_client.flushdb()
    except Exception as e:
        print(f"Lỗi khi xóa toàn bộ cache: {e}")
        return False 