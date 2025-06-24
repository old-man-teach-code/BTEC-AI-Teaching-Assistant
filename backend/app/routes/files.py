from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Path
from typing import List, Optional
from services.file_service import save_file, delete_file, list_files, validate_file
from schemas.file import FileResponse, FileListResponse, FileDeleteResponse
from dependencies.deps import get_current_user

router = APIRouter()

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    subfolder: Optional[str] = Query(None, description="Thư mục con trong uploads để lưu file"),
    current_user = Depends(get_current_user)
):
    """
    Upload một file vào hệ thống
    
    - **file**: File cần upload
    - **subfolder**: (Tùy chọn) Thư mục con trong uploads để lưu file
    """
    result = await save_file(file, subfolder)
    return result

@router.get("/list", response_model=FileListResponse)
def get_files(
    subfolder: Optional[str] = Query(None, description="Thư mục con trong uploads để liệt kê file"),
    current_user = Depends(get_current_user)
):
    """
    Liệt kê tất cả các file trong thư mục uploads hoặc subfolder
    
    - **subfolder**: (Tùy chọn) Thư mục con trong uploads để liệt kê file
    """
    files = list_files(subfolder)
    return {
        "files": files,
        "total": len(files)
    }

@router.delete("/{file_path:path}", response_model=FileDeleteResponse)
def remove_file(
    file_path: str = Path(..., description="Đường dẫn tương đối của file trong thư mục uploads"),
    current_user = Depends(get_current_user)
):
    """
    Xóa một file từ hệ thống
    
    - **file_path**: Đường dẫn tương đối của file trong thư mục uploads
    """
    success = delete_file(file_path)
    
    if success:
        return {
            "success": True,
            "message": f"Đã xóa file: {file_path}"
        }
    else:
        return {
            "success": False,
            "message": f"Không thể xóa file: {file_path}. File không tồn tại hoặc có lỗi xảy ra."
        } 