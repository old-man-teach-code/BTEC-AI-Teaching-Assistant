import logging
import re
from typing import List, Dict, Any, Optional, Tuple
import json

from core.llm_config import get_llm, llm_manager
from core.config import settings

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Service xử lý template và điền thông tin
    Hỗ trợ extract variables, validate, và fill template với LLM
    """
    
    def __init__(self):
        # Pattern để tìm variables trong template
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')
        
        # Common variables và descriptions
        self.common_variables = {
            "student_name": "Tên sinh viên",
            "subject": "Tên môn học",
            "course_code": "Mã môn học",
            "deadline": "Thời hạn nộp bài",
            "assignment_name": "Tên bài tập/assignment",
            "score": "Điểm số",
            "date": "Ngày tháng",
            "time": "Thời gian",
            "location": "Địa điểm",
            "teacher_name": "Tên giảng viên",
            "note": "Ghi chú",
            "requirement": "Yêu cầu",
            "class_name": "Tên lớp",
            "semester": "Học kỳ",
            "academic_year": "Năm học"
        }
    
    def extract_variables(self, template_content: str) -> List[str]:
        """
        Extract tất cả variables từ template
        
        Args:
            template_content: Nội dung template
            
        Returns:
            List tên variables (unique)
        """
        matches = self.variable_pattern.findall(template_content)
        # Remove duplicates while preserving order
        seen = set()
        unique_vars = []
        for var in matches:
            if var not in seen:
                seen.add(var)
                unique_vars.append(var)
        
        return unique_vars
    
    def validate_template_syntax(self, template_content: str) -> Tuple[bool, List[str]]:
        """
        Validate syntax của template
        
        Args:
            template_content: Nội dung template
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for unclosed brackets
        open_count = template_content.count('{{')
        close_count = template_content.count('}}')
        
        if open_count != close_count:
            errors.append(f"Số dấu mở '{{{{' ({open_count}) không khớp với số dấu đóng '}}}}' ({close_count})")
        
        # Check for empty variables
        empty_vars = re.findall(r'\{\{\s*\}\}', template_content)
        if empty_vars:
            errors.append("Template chứa biến rỗng: {{}}")
        
        # Check for invalid variable names
        all_matches = re.findall(r'\{\{([^}]*)\}\}', template_content)
        for match in all_matches:
            if not re.match(r'^\w+$', match.strip()):
                errors.append(f"Tên biến không hợp lệ: '{match}'. Chỉ được dùng chữ cái, số và dấu gạch dưới")
        
        # Check for nested variables
        if re.search(r'\{\{[^}]*\{\{', template_content):
            errors.append("Template chứa biến lồng nhau, không được hỗ trợ")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def analyze_variable(self, variable_name: str) -> Dict[str, Any]:
        """
        Phân tích một variable và đưa ra thông tin
        
        Args:
            variable_name: Tên variable
            
        Returns:
            Dict chứa thông tin về variable
        """
        info = {
            "name": variable_name,
            "description": self.common_variables.get(variable_name, "Biến tùy chỉnh"),
            "required": True,
            "default_value": None,
            "type": "string"  # Default type
        }
        
        # Infer type từ tên biến
        if any(keyword in variable_name.lower() for keyword in ["date", "deadline", "ngay"]):
            info["type"] = "date"
        elif any(keyword in variable_name.lower() for keyword in ["time", "gio"]):
            info["type"] = "time"
        elif any(keyword in variable_name.lower() for keyword in ["score", "diem", "number", "so"]):
            info["type"] = "number"
        elif any(keyword in variable_name.lower() for keyword in ["note", "ghi_chu", "description"]):
            info["required"] = False
        
        return info
    
    def is_standard_variable(self, variable_name: str) -> bool:
        """
        Kiểm tra variable có phải là standard không
        
        Args:
            variable_name: Tên variable
            
        Returns:
            True nếu là standard variable
        """
        return variable_name in self.common_variables
    
    def suggest_standard_name(self, variable_name: str) -> str:
        """
        Gợi ý tên chuẩn cho variable
        
        Args:
            variable_name: Tên variable hiện tại
            
        Returns:
            Tên chuẩn được gợi ý
        """
        lower_name = variable_name.lower()
        
        # Mapping common variations
        mappings = {
            "ten_sv": "student_name",
            "tensv": "student_name",
            "ten_sinh_vien": "student_name",
            "hoten": "student_name",
            "monhoc": "subject",
            "mon": "subject",
            "ma_mon": "course_code",
            "mamh": "course_code",
            "han_nop": "deadline",
            "hannop": "deadline",
            "thoi_han": "deadline",
            "diem_so": "score",
            "diemso": "score",
            "ngay": "date",
            "thoi_gian": "time",
            "thoigian": "time",
            "dia_diem": "location",
            "diadiem": "location",
            "ghi_chu": "note",
            "ghichu": "note",
            "yeu_cau": "requirement",
            "yeucau": "requirement"
        }
        
        # Direct mapping
        if lower_name in mappings:
            return mappings[lower_name]
        
        # Partial matching
        for key, value in mappings.items():
            if key in lower_name or lower_name in key:
                return value
        
        # No suggestion, return original
        return variable_name
    
    def create_search_query(
        self,
        question: str,
        variables: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Tạo search query từ câu hỏi và variables cần điền
        
        Args:
            question: Câu hỏi từ user
            variables: List variables cần tìm thông tin
            context: Context bổ sung
            
        Returns:
            Optimized search query
        """
        # Start với câu hỏi gốc
        query_parts = [question]
        
        # Add context nếu có
        if context:
            for key, value in context.items():
                if isinstance(value, str) and value:
                    query_parts.append(value)
        
        # Add variable hints
        for var in variables:
            if var in self.common_variables:
                # Add Vietnamese description
                query_parts.append(self.common_variables[var])
        
        # Join và clean up
        query = " ".join(query_parts)
        
        # Remove duplicates và common words
        words = query.split()
        seen = set()
        unique_words = []
        
        common_words = {"là", "gì", "khi", "nào", "của", "cho", "và", "hoặc", "với"}
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in seen and word_lower not in common_words:
                seen.add(word_lower)
                unique_words.append(word)
        
        # Limit query length
        query = " ".join(unique_words[:20])  # Max 20 words
        
        return query
    
    async def fill_template_with_llm(
        self,
        template: str,
        variables: List[str],
        question: str,
        context: Optional[Dict[str, Any]] = None,
        relevant_info: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Sử dụng LLM để điền template
        
        Args:
            template: Template content
            variables: List variables cần điền
            question: Câu hỏi từ user
            context: Context dictionary
            relevant_info: Thông tin từ RAG
            
        Returns:
            Dict với filled_content và variables_filled
        """
        try:
            # Prepare context cho LLM
            llm_context = []
            
            # Add user context
            if context:
                llm_context.append("Thông tin context:")
                for key, value in context.items():
                    llm_context.append(f"- {key}: {value}")
            
            # Add relevant info từ RAG
            if relevant_info:
                llm_context.append("\nThông tin liên quan từ knowledge base:")
                for i, info in enumerate(relevant_info[:5]):  # Limit to 5
                    llm_context.append(f"{i+1}. {info[:200]}...")  # Truncate long text
            
            # Create prompt
            prompt = self._create_fill_prompt(
                template=template,
                variables=variables,
                question=question,
                context_str="\n".join(llm_context) if llm_context else "Không có context bổ sung"
            )
            
            # Call LLM
            llm = get_llm()
            response = llm.complete(prompt, temperature=0.3)  # Lower temperature for consistency
            
            # Parse response
            filled_result = self._parse_llm_response(response.text, template, variables)
            
            return filled_result
            
        except Exception as e:
            logger.error(f"Error filling template with LLM: {str(e)}")
            # Fallback: return template with empty values
            return {
                "filled_content": template,
                "variables_filled": {var: "[Không tìm thấy thông tin]" for var in variables}
            }
    
    def _create_fill_prompt(
        self,
        template: str,
        variables: List[str],
        question: str,
        context_str: str
    ) -> str:
        """
        Tạo prompt cho LLM để điền template
        
        Args:
            template: Template content
            variables: List variables
            question: User question
            context_str: Context information
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Bạn là trợ lý giúp điền thông tin vào template câu trả lời.

NHIỆM VỤ:
Dựa vào câu hỏi và thông tin được cung cấp, hãy điền các biến trong template để tạo câu trả lời hoàn chỉnh.

CÂU HỎI TỪ NGƯỜI DÙNG:
{question}

TEMPLATE CẦN ĐIỀN:
{template}

CÁC BIẾN CẦN ĐIỀN:
{', '.join([f'{{{{{var}}}}}' for var in variables])}

THÔNG TIN THAM KHẢO:
{context_str}

YÊU CẦU:
1. Điền thông tin chính xác vào các biến dựa trên thông tin được cung cấp
2. Nếu không tìm thấy thông tin cho biến nào, hãy điền "[Không có thông tin]"
3. Đảm bảo câu trả lời tự nhiên và phù hợp ngữ cảnh
4. Trả về kết quả theo format JSON sau:

{{
    "filled_template": "Template đã điền đầy đủ",
    "variables": {{
        "tên_biến_1": "giá trị 1",
        "tên_biến_2": "giá trị 2"
    }}
}}

Hãy điền template:"""
        
        return prompt
    
    def _parse_llm_response(
        self,
        llm_response: str,
        template: str,
        variables: List[str]
    ) -> Dict[str, Any]:
        """
        Parse response từ LLM
        
        Args:
            llm_response: Raw response từ LLM
            template: Original template
            variables: List variables
            
        Returns:
            Parsed result
        """
        try:
            # Try to parse JSON response
            # Find JSON block in response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                filled_template = parsed.get("filled_template", template)
                variables_dict = parsed.get("variables", {})
                
                return {
                    "filled_content": filled_template,
                    "variables_filled": variables_dict
                }
        except:
            logger.warning("Cannot parse JSON from LLM response, using fallback")
        
        # Fallback: Try to extract values manually
        filled_template = template
        variables_filled = {}
        
        # Simple extraction từ response text
        for var in variables:
            # Look for pattern like "variable_name: value" or "{{variable_name}}: value"
            patterns = [
                rf'{var}:\s*([^\n]+)',
                rf'{{{{{var}}}}}:\s*([^\n]+)',
                rf'"{var}":\s*"([^"]+)"'
            ]
            
            value = None
            for pattern in patterns:
                match = re.search(pattern, llm_response, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    break
            
            if value:
                variables_filled[var] = value
                filled_template = filled_template.replace(f"{{{{{var}}}}}", value)
            else:
                variables_filled[var] = "[Không có thông tin]"
                filled_template = filled_template.replace(f"{{{{{var}}}}}", "[Không có thông tin]")
        
        return {
            "filled_content": filled_template,
            "variables_filled": variables_filled
        }
    
    def calculate_confidence(
        self,
        filled_variables: Dict[str, str],
        required_variables: List[str],
        has_rag_support: bool = False
    ) -> float:
        """
        Tính confidence score cho filled template
        
        Args:
            filled_variables: Dict các biến đã điền
            required_variables: List biến cần điền
            has_rag_support: Có thông tin từ RAG không
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        if not required_variables:
            return 1.0
        
        # Base score từ tỷ lệ biến được điền
        filled_count = 0
        for var in required_variables:
            value = filled_variables.get(var, "")
            if value and value != "[Không có thông tin]":
                filled_count += 1
        
        base_score = filled_count / len(required_variables)
        
        # Bonus nếu có RAG support
        if has_rag_support:
            base_score = min(1.0, base_score + 0.1)
        
        # Penalty nếu nhiều biến không có thông tin
        empty_count = len(required_variables) - filled_count
        if empty_count > len(required_variables) / 2:
            base_score *= 0.8
        
        return round(base_score, 2)