import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from core.config import settings

# Danh sách các phần mở rộng file được chấp nhận
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.pptx']
# Kích thước file tối đa (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

def get_file_extension(filename: str) -> str:
    """
    Lấy phần mở rộng của file
    
    Args:
        filename: Tên file cần kiểm tra
        
    Returns:
        str: Phần mở rộng của file (bao gồm dấu chấm)
    """
    return os.path.splitext(filename)[1].lower()

def get_file_size(file: UploadFile) -> int:
    """
    Lấy kích thước của file
    
    Args:
        file: File cần kiểm tra kích thước
        
    Returns:
        int: Kích thước file tính bằng bytes
    """
    # Lưu vị trí hiện tại của con trỏ file
    current_position = file.file.tell()
    
    # Di chuyển đến cuối file để lấy kích thước
    file.file.seek(0, 2)  # 0 từ cuối file
    size = file.file.tell()
    
    # Trở lại vị trí ban đầu
    file.file.seek(current_position)
    
    return size

def validate_file(file: UploadFile) -> Optional[str]:
    """
    Kiểm tra tính hợp lệ của file
    
    Args:
        file: File cần kiểm tra
        
    Returns:
        Optional[str]: Thông báo lỗi nếu file không hợp lệ, None nếu hợp lệ
    """
    # Kiểm tra phần mở rộng
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        return f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Kiểm tra kích thước
    size = get_file_size(file)
    if size > MAX_FILE_SIZE:
        return f"Kích thước file quá lớn. Tối đa {MAX_FILE_SIZE / (1024 * 1024)}MB"
    
    return None

def save_file(file: UploadFile) -> str:
    """
    Lưu file đã tải lên vào hệ thống
    
    Args:
        file: File cần lưu
        
    Returns:
        str: Đường dẫn đến file đã lưu
    """
    # Kiểm tra tính hợp lệ của file
    error = validate_file(file)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Đảm bảo thư mục uploads tồn tại
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True)
    
    # Tạo tên file duy nhất
    ext = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_filename
    
    # Lưu file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)

def delete_file(file_path: str) -> bool:
    """
    Xóa file từ hệ thống
    
    Args:
        file_path: Đường dẫn đến file cần xóa
        
    Returns:
        bool: True nếu xóa thành công, False nếu không
    """
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            return True
        return False
    except Exception as e:
        return False 