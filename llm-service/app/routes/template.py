import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import time

from models.schemas import (
    TemplateFillRequest,
    FilledTemplate,
    TemplateAnalysisRequest,
    TemplateAnalysisResponse,
    TemplateVariable,
    ErrorResponse
)
from services.template_service import TemplateService
from services.rag_service import RAGService
from database.mysql_client import get_mysql_client, MySQLClient
from core.config import settings

logger = logging.getLogger(__name__)

# Khởi tạo router
router = APIRouter()

# Khởi tạo services
template_service = TemplateService()
rag_service = RAGService()


@router.post("/fill", response_model=FilledTemplate)
async def fill_template(
    request: TemplateFillRequest,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Điền thông tin vào template dựa trên câu hỏi và RAG
    
    Quy trình xử lý:
    1. Lấy template từ backend database
    2. Phân tích câu hỏi để hiểu context
    3. Tìm kiếm thông tin liên quan từ RAG
    4. Sử dụng LLM để điền các biến trong template
    5. Trả về template đã điền đầy đủ
    
    Args:
        request: Template fill request
        mysql: MySQL client dependency
        
    Returns:
        FilledTemplate: Template đã được điền
        
    Example:
        Input:
            - Template: "Deadline môn {{subject}} là {{deadline}}"
            - Question: "Deadline ASM môn toán lớp SE07102 là khi nào?"
            
        Output:
            - Filled: "Deadline môn Toán cao cấp là 23:59 ngày 31/07/2025"
    """
    try:
        # Kiểm tra user tồn tại
        if not mysql.check_user_exists(request.user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User với ID {request.user_id} không tồn tại"
            )
        
        # Lấy template từ database
        template_info = mysql.get_template_by_id(request.template_id)
        if not template_info:
            raise HTTPException(
                status_code=404,
                detail=f"Template với ID {request.template_id} không tồn tại"
            )
        
        # Kiểm tra quyền truy cập template
        if template_info["owner_id"] != request.user_id:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền sử dụng template này"
            )
        
        # Bước 1: Phân tích template để tìm variables
        template_content = template_info["content"]
        variables = template_service.extract_variables(template_content)
        
        if not variables:
            # Template không có biến, trả về nguyên bản
            return FilledTemplate(
                template_id=request.template_id,
                original_template=template_content,
                filled_content=template_content,
                variables_filled={},
                confidence_score=1.0,
                sources=[]
            )
        
        # Bước 2: Tìm kiếm thông tin từ RAG nếu được yêu cầu
        relevant_info = []
        sources = []
        
        if request.use_rag:
            # Tạo query từ câu hỏi và variables
            search_query = template_service.create_search_query(
                question=request.question,
                variables=variables,
                context=request.context
            )
            
            # Search trong RAG
            search_results = await rag_service.search(
                query=search_query,
                user_id=request.user_id,
                top_k=settings.top_k_results
            )
            
            # Extract relevant information
            for result in search_results:
                relevant_info.append(result.text)
                if result.source:
                    sources.append(result.source)
        
        # Bước 3: Sử dụng LLM để điền template
        filled_result = await template_service.fill_template_with_llm(
            template=template_content,
            variables=variables,
            question=request.question,
            context=request.context,
            relevant_info=relevant_info
        )
        
        # Bước 4: Tính confidence score
        confidence_score = template_service.calculate_confidence(
            filled_variables=filled_result["variables_filled"],
            required_variables=variables,
            has_rag_support=len(relevant_info) > 0
        )
        
        return FilledTemplate(
            template_id=request.template_id,
            original_template=template_content,
            filled_content=filled_result["filled_content"],
            variables_filled=filled_result["variables_filled"],
            confidence_score=confidence_score,
            sources=list(set(sources))  # Remove duplicates
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi fill template: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.post("/analyze", response_model=TemplateAnalysisResponse)
async def analyze_template(request: TemplateAnalysisRequest):
    """
    Phân tích template để tìm variables và đưa ra suggestions
    
    Chức năng:
    - Tìm tất cả variables trong template (format {{variable_name}})
    - Đề xuất tên biến chuẩn
    - Kiểm tra syntax của template
    - Gợi ý cải thiện template
    
    Args:
        request: Template analysis request
        
    Returns:
        TemplateAnalysisResponse: Kết quả phân tích
    """
    try:
        # Extract variables
        variables = template_service.extract_variables(request.template_content)
        
        # Analyze each variable
        variable_details = []
        for var in variables:
            # Xác định loại variable và mô tả
            var_info = template_service.analyze_variable(var)
            
            variable_details.append(TemplateVariable(
                name=var,
                description=var_info.get("description"),
                required=var_info.get("required", True),
                default_value=var_info.get("default_value")
            ))
        
        # Validate template syntax
        is_valid, validation_errors = template_service.validate_template_syntax(
            request.template_content
        )
        
        # Generate suggestions
        suggestions = []
        
        # Suggestion về tên biến
        for var in variables:
            if not template_service.is_standard_variable(var):
                standard_name = template_service.suggest_standard_name(var)
                if standard_name != var:
                    suggestions.append(
                        f"Cân nhắc đổi tên biến '{var}' thành '{standard_name}' "
                        f"để phù hợp với quy chuẩn"
                    )
        
        # Suggestion về cấu trúc template
        if len(request.template_content) < 20:
            suggestions.append(
                "Template quá ngắn, cân nhắc thêm context để câu trả lời tự nhiên hơn"
            )
        
        if "{{" in request.template_content and "}}" not in request.template_content:
            suggestions.append(
                "Template có vẻ thiếu dấu đóng '}}' cho biến"
            )
        
        # Suggestion về duplicate variables
        duplicate_vars = [var for var in variables if variables.count(var) > 1]
        if duplicate_vars:
            suggestions.append(
                f"Biến '{duplicate_vars[0]}' xuất hiện nhiều lần trong template"
            )
        
        # Add validation errors to suggestions
        suggestions.extend(validation_errors)
        
        return TemplateAnalysisResponse(
            variables=variables,
            variable_details=variable_details,
            template_valid=is_valid,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Lỗi khi analyze template: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.post("/preview/{template_id}")
async def preview_filled_template(
    template_id: int,
    sample_data: Dict[str, Any],
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Preview template với sample data (không dùng RAG)
    
    Chức năng test nhanh template với dữ liệu mẫu
    
    Args:
        template_id: ID của template
        sample_data: Dữ liệu mẫu để điền vào template
        mysql: MySQL client dependency
        
    Returns:
        Preview result
    """
    try:
        # Lấy template từ database
        template_info = mysql.get_template_by_id(template_id)
        if not template_info:
            raise HTTPException(
                status_code=404,
                detail=f"Template với ID {template_id} không tồn tại"
            )
        
        template_content = template_info["content"]
        
        # Simple replacement
        filled_content = template_content
        for var_name, var_value in sample_data.items():
            placeholder = "{{" + var_name + "}}"
            filled_content = filled_content.replace(placeholder, str(var_value))
        
        # Check for unfilled variables
        remaining_vars = template_service.extract_variables(filled_content)
        
        return {
            "template_id": template_id,
            "original": template_content,
            "preview": filled_content,
            "sample_data": sample_data,
            "unfilled_variables": remaining_vars
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi preview template: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.get("/common-variables")
async def get_common_variables():
    """
    Lấy danh sách các biến phổ biến được khuyên dùng
    
    Returns:
        List of common variables với description
    """
    common_vars = [
        {
            "name": "student_name",
            "description": "Tên sinh viên",
            "example": "Nguyễn Văn A"
        },
        {
            "name": "subject",
            "description": "Tên môn học",
            "example": "Toán cao cấp"
        },
        {
            "name": "course_code",
            "description": "Mã môn học",
            "example": "SE07102"
        },
        {
            "name": "deadline",
            "description": "Thời hạn nộp bài",
            "example": "23:59 ngày 31/07/2025"
        },
        {
            "name": "assignment_name",
            "description": "Tên bài tập/assignment",
            "example": "Assignment 1"
        },
        {
            "name": "score",
            "description": "Điểm số",
            "example": "8.5/10"
        },
        {
            "name": "date",
            "description": "Ngày tháng chung",
            "example": "15/01/2025"
        },
        {
            "name": "time",
            "description": "Thời gian",
            "example": "14:30"
        },
        {
            "name": "location",
            "description": "Địa điểm",
            "example": "Phòng 201, Tòa A"
        },
        {
            "name": "teacher_name",
            "description": "Tên giảng viên",
            "example": "TS. Phạm Văn B"
        },
        {
            "name": "note",
            "description": "Ghi chú thêm",
            "example": "Lưu ý mang theo laptop"
        },
        {
            "name": "requirement",
            "description": "Yêu cầu",
            "example": "Nộp file PDF, tối đa 10 trang"
        }
    ]
    
    return {
        "total": len(common_vars),
        "variables": common_vars
    }


@router.post("/batch-fill")
async def batch_fill_templates(
    requests: List[TemplateFillRequest],
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Điền nhiều templates cùng lúc
    
    Hữu ích khi cần xử lý nhiều câu hỏi tương tự
    
    Args:
        requests: List of template fill requests
        mysql: MySQL client dependency
        
    Returns:
        Batch results
    """
    if len(requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Tối đa 10 templates mỗi batch"
        )
    
    results = []
    
    for req in requests:
        try:
            # Process each template
            result = await fill_template(req, mysql)
            results.append({
                "success": True,
                "template_id": req.template_id,
                "result": result
            })
        except Exception as e:
            logger.error(f"Lỗi fill template {req.template_id}: {str(e)}")
            results.append({
                "success": False,
                "template_id": req.template_id,
                "error": str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "results": results
    }