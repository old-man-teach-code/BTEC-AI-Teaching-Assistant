import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from fastapi import UploadFile, HTTPException
from core.config import settings

def get_file_extension(filename: str) -> str:
    """
    Lấy phần mở rộng của file
    
    Args:
        filename: Tên file cần lấy phần mở rộng
        
    Returns:
        Phần mở rộng của file (bao gồm dấu chấm)
    """
    return os.path.splitext(filename)[1].lower()

def get_file_size(file: UploadFile) -> int:
    """
    Lấy kích thước của file
    
    Args:
        file: File cần kiểm tra kích thước
        
    Returns:
        Kích thước của file (bytes)
    """
    # Lưu vị trí hiện tại của con trỏ file
    current_position = file.file.tell()
    
    # Di chuyển đến cuối file để lấy kích thước
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    
    # Trở lại vị trí ban đầu
    file.file.seek(current_position)
    
    return size

def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra tính hợp lệ của file
    
    Args:
        file: File cần kiểm tra
        
    Returns:
        Tuple[bool, Optional[str]]: (file có hợp lệ không, thông báo lỗi nếu không hợp lệ)
    """
    # Kiểm tra phần mở rộng
    extension = get_file_extension(file.filename)
    if extension not in settings.ALLOWED_EXTENSIONS:
        return False, f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(settings.ALLOWED_EXTENSIONS)}"
    
    # Kiểm tra kích thước
    size = get_file_size(file)
    if size > settings.MAX_FILE_SIZE:
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        return False, f"Kích thước file vượt quá giới hạn cho phép ({max_size_mb:.1f}MB)"
    
    return True, None

async def save_file(file: UploadFile, subfolder: str = "") -> Dict[str, Any]:
    """
    Lưu file tải lên vào thư mục uploads
    
    Args:
        file: File cần lưu
        subfolder: Thư mục con trong uploads (nếu có)
        
    Returns:
        Dict chứa thông tin về file đã lưu (path, filename, size, extension)
        
    Raises:
        HTTPException: Nếu file không hợp lệ
    """
    # Kiểm tra tính hợp lệ của file
    is_valid, error_message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Tạo tên file duy nhất
    extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{extension}"
    
    # Tạo đường dẫn đầy đủ
    upload_dir = settings.UPLOAD_DIR
    if subfolder:
        upload_dir = upload_dir / subfolder
    
    # Đảm bảo thư mục tồn tại
    os.makedirs(upload_dir, exist_ok=True)
    
    # Đường dẫn đầy đủ đến file
    file_path = upload_dir / unique_filename
    
    # Lưu file
    try:
        # Đọc nội dung file
        contents = await file.read()
        
        # Ghi nội dung vào file mới
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Đặt lại vị trí file để có thể đọc lại nếu cần
        await file.seek(0)
        
        # Đường dẫn tương đối so với thư mục gốc uploads
        relative_path = os.path.join(subfolder, unique_filename) if subfolder else unique_filename
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": get_file_size(file),
            "path": str(relative_path),
            "full_path": str(file_path)
        }
    except Exception as e:
        # Xử lý lỗi khi lưu file
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")

def delete_file(file_path: str) -> bool:
    """
    Xóa file từ hệ thống
    
    Args:
        file_path: Đường dẫn tương đối của file trong thư mục uploads
        
    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi
    """
    try:
        # Tạo đường dẫn đầy đủ
        full_path = settings.UPLOAD_DIR / file_path
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(full_path):
            return False
        
        # Xóa file
        os.remove(full_path)
        return True
    except Exception as e:
        print(f"Lỗi khi xóa file {file_path}: {str(e)}")
        return False

def list_files(subfolder: str = "") -> List[Dict[str, Any]]:
    """
    Liệt kê tất cả các file trong thư mục uploads hoặc subfolder
    
    Args:
        subfolder: Thư mục con trong uploads (nếu có)
        
    Returns:
        List[Dict]: Danh sách thông tin các file
    """
    try:
        # Tạo đường dẫn đầy đủ
        directory = settings.UPLOAD_DIR
        if subfolder:
            directory = directory / subfolder
        
        # Kiểm tra thư mục có tồn tại không
        if not os.path.exists(directory):
            return []
        
        # Liệt kê các file
        files = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Chỉ lấy file, không lấy thư mục
            if os.path.isfile(file_path):
                relative_path = os.path.join(subfolder, filename) if subfolder else filename
                files.append({
                    "filename": filename,
                    "path": relative_path,
                    "size": os.path.getsize(file_path),
                    "extension": get_file_extension(filename)
                })
                
        return files
    except Exception as e:
        print(f"Lỗi khi liệt kê file: {str(e)}")
        return [] 