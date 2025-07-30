import logging
from typing import Optional, Any
from pathlib import Path
from llama_cpp import Llama
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core.llms import ChatMessage

from core.config import settings

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Quản lý Large Language Model
    Sử dụng llama-cpp-python để load model GGUF
    """
    
    def __init__(self):
        self.llm: Optional[LlamaCPP] = None
        self.raw_model: Optional[Llama] = None
        
    def initialize(self) -> None:
        """
        Khởi tạo LLM từ file GGUF
        Model: Arcee-VyLinh (Vietnamese optimized)
        """
        try:
            model_path = Path(settings.model_path)
            
            # Kiểm tra file model tồn tại
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Không tìm thấy model tại: {model_path}\n"
                    f"Vui lòng download model và đặt vào thư mục: {model_path.parent}"
                )
            
            logger.info(f"Đang load model từ: {model_path}")
            
            # Cấu hình model parameters
            model_kwargs = {
                "model_path": str(model_path),
                "n_ctx": settings.llm_context_size,  # Context window
                "n_threads": 4,  # Số threads CPU sử dụng
                "n_gpu_layers": settings.llm_n_gpu_layers,  # GPU layers (0 = CPU only)
                "verbose": settings.log_level == "DEBUG",
                "seed": 42,  # Để có kết quả nhất quán
                "f16_kv": True,  # Sử dụng float16 cho key-value cache
                "logits_all": False,
                "vocab_only": False,
                "use_mlock": False,  # Không lock memory
                "n_batch": 512,  # Batch size cho prompt processing
            }
            
            # Khởi tạo raw model (llama-cpp-python)
            self.raw_model = Llama(**model_kwargs)
            
            # Wrap với LlamaIndex interface
            self.llm = LlamaCPP(
                model_path=str(model_path),
                temperature=settings.llm_temperature,
                max_new_tokens=settings.llm_max_tokens,
                context_window=settings.llm_context_size,
                generate_kwargs={
                    "temperature": settings.llm_temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                },
                model_kwargs=model_kwargs,
                verbose=settings.log_level == "DEBUG"
            )
            
            logger.info("✅ LLM khởi tạo thành công!")
            
            # Test model
            self._test_model()
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi tạo LLM: {str(e)}")
            raise
    
    def _test_model(self) -> None:
        """Test model với câu hỏi đơn giản"""
        try:
            test_prompt = "Xin chào, bạn là ai?"
            response = self.generate(test_prompt)
            logger.info(f"Test LLM thành công. Response: {response[:100]}...")
        except Exception as e:
            logger.error(f"Test LLM thất bại: {str(e)}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response từ prompt
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text
        """
        if not self.llm:
            raise RuntimeError("LLM chưa được khởi tạo!")
        
        # Merge với default parameters
        generation_kwargs = {
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
        }
        generation_kwargs.update(kwargs)
        
        # Generate response
        response = self.llm.complete(prompt, **generation_kwargs)
        
        return response.text
    
    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Chat completion với history
        
        Args:
            messages: List of chat messages [{"role": "user/assistant", "content": "..."}]
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        if not self.llm:
            raise RuntimeError("LLM chưa được khởi tạo!")
        
        # Convert to LlamaIndex ChatMessage format
        chat_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            chat_messages.append(ChatMessage(role=role, content=content))
        
        # Generate response
        response = self.llm.chat(chat_messages, **kwargs)
        
        return response.message.content
    
    def get_model_info(self) -> dict:
        """Lấy thông tin về model"""
        if not self.llm:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "model_path": str(settings.model_path),
            "context_size": settings.llm_context_size,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "n_gpu_layers": settings.llm_n_gpu_layers,
        }
    
    def create_prompt_template(self, instruction: str, context: str = "", question: str = "") -> str:
        """
        Tạo prompt template chuẩn cho model
        Sử dụng format phù hợp với model tiếng Việt
        
        Args:
            instruction: Hướng dẫn cho model
            context: Context/Knowledge từ RAG
            question: Câu hỏi cụ thể từ user
            
        Returns:
            Formatted prompt
        """
        prompt_parts = []
        
        # System instruction
        prompt_parts.append(f"### Hướng dẫn:\n{instruction}")
        
        # Context từ RAG
        if context:
            prompt_parts.append(f"\n### Ngữ cảnh:\n{context}")
        
        # User question
        if question:
            prompt_parts.append(f"\n### Câu hỏi:\n{question}")
        
        # Response instruction
        prompt_parts.append("\n### Trả lời:")
        
        return "\n".join(prompt_parts)


# Singleton instance
llm_manager = LLMManager()


def initialize_llm():
    """Initialize LLM - được gọi từ main.py"""
    llm_manager.initialize()


def get_llm() -> LlamaCPP:
    """Get LLM instance cho dependency injection"""
    if not llm_manager.llm:
        raise RuntimeError("LLM chưa được khởi tạo!")
    return llm_manager.llm