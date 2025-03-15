"""LLM管理器模块"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class LLMProvider(str, Enum):
    """LLM提供商"""
    OPENAI = "openai"
    AZURE = "azure"
    CUSTOM = "custom"

class LLMConfig(BaseModel):
    """LLM配置"""
    provider: LLMProvider
    api_key: str
    api_base: Optional[str] = None
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    timeout: int = Field(default=30, description="请求超时时间(秒)")
    extra_params: Dict[str, Any] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应"""
    message: ChatMessage
    usage: Dict[str, int]
    raw_response: Dict[str, Any]

class BaseLLM(ABC):
    """LLM基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """聊天接口"""
        pass

class OpenAILLM(BaseLLM):
    """OpenAI LLM实现"""
    
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        import openai
        
        openai.api_key = self.config.api_key
        if self.config.api_base:
            openai.api_base = self.config.api_base
            
        try:
            # 转换消息格式
            openai_messages = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    **({
                        "name": msg.name
                    } if msg.name else {}),
                    **({
                        "function_call": msg.function_call
                    } if msg.function_call else {})
                } for msg in messages
            ]
            
            # 调用API
            response = await openai.ChatCompletion.acreate(
                model=self.config.model,
                messages=openai_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **self.config.extra_params
            )
            
            # 解析响应
            choice = response.choices[0]
            message = ChatMessage(
                role=choice.message.role,
                content=choice.message.content,
                name=getattr(choice.message, "name", None),
                function_call=getattr(choice.message, "function_call", None)
            )
            
            return ChatResponse(
                message=message,
                usage=response.usage,
                raw_response=response
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")

class AzureLLM(BaseLLM):
    """Azure LLM实现"""
    
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        # TODO: 实现Azure API调用
        pass

class CustomLLM(BaseLLM):
    """自定义LLM实现"""
    
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        # TODO: 实现自定义API调用
        pass

class LLMManager:
    """LLM管理器"""
    
    _instances: Dict[str, BaseLLM] = {}
    
    @classmethod
    def create_llm(cls, config: LLMConfig) -> BaseLLM:
        """创建LLM实例"""
        provider_map = {
            LLMProvider.OPENAI: OpenAILLM,
            LLMProvider.AZURE: AzureLLM,
            LLMProvider.CUSTOM: CustomLLM,
        }
        
        llm_class = provider_map.get(config.provider)
        if not llm_class:
            raise ValueError(f"不支持的LLM提供商: {config.provider}")
        
        return llm_class(config)
    
    @classmethod
    def get_llm(cls, name: str = "default") -> BaseLLM:
        """获取LLM实例"""
        if name not in cls._instances:
            raise KeyError(f"LLM实例不存在: {name}")
        return cls._instances[name]
    
    @classmethod
    def register_llm(cls, name: str, llm: BaseLLM) -> None:
        """注册LLM实例"""
        cls._instances[name] = llm
    
    @classmethod
    def remove_llm(cls, name: str) -> None:
        """移除LLM实例"""
        if name in cls._instances:
            del cls._instances[name]