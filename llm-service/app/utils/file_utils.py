import os
import aiofiles
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_file_extension(filename: str) -> str:
    """
    Lấy extension của file
    
    Args:
        filename: Tên file
        
    Returns:
        Extension (bao gồm dấu chấm, vd: '.pdf')
    """
    return os.path.splitext(filename)[1].lower()


def get_file_size_mb(file_path: str) -> float:
    """
    Lấy kích thước file tính bằng MB
    
    Args:
        file_path: Đường dẫn file
        
    Returns:
        Kích thước file (MB)
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0


async def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Đọc nội dung text file async
    
    Args:
        file_path: Đường dẫn file
        encoding: Encoding của file
        
    Returns:
        Nội dung file
    """
    try:
        async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
            content = await f.read()
        return content
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            async with aiofiles.open(file_path, mode='r', encoding='latin-1') as f:
                content = await f.read()
            return content
        except Exception as e:
            logger.error(f"Cannot read file {file_path}: {str(e)}")
            return ""
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""


def validate_file_path(file_path: str) -> bool:
    """
    Kiểm tra file path có hợp lệ và an toàn không
    
    Args:
        file_path: Đường dẫn cần kiểm tra
        
    Returns:
        True nếu hợp lệ
    """
    # Check file exists
    if not os.path.exists(file_path):
        return False
    
    # Check is file (not directory)
    if not os.path.isfile(file_path):
        return False
    
    # Check for path traversal
    abs_path = os.path.abspath(file_path)
    if '..' in abs_path:
        return False
    
    return True


def ensure_directory(directory: str) -> None:
    """
    Đảm bảo directory tồn tại
    
    Args:
        directory: Đường dẫn directory
    """
    os.makedirs(directory, exist_ok=True)


def clean_filename(filename: str) -> str:
    """
    Clean filename để an toàn khi lưu
    
    Args:
        filename: Tên file gốc
        
    Returns:
        Tên file đã clean
    """
    # Remove special characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext