"""
工具管理模块
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type

from pydantic import BaseModel, Field


class ToolCategory(str, Enum):
    """工具类别"""
    FILE = "file"
    CODE = "code"
    BROWSER = "browser"
    SYSTEM = "system"


class ToolMetadata(BaseModel):
    """工具元数据"""
    name: str
    description: str
    category: ToolCategory
    version: str
    author: str
    risk_level: str
    os_compatibility: List[str]
    dependencies: List[str]
    parameters: Dict[str, Any]
    timeout: int = Field(default=30, description="执行超时时间(秒)")


class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = Field(default=0.0, description="执行时间(秒)")


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self):
        self.metadata = self.get_metadata()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """获取工具元数据"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        return True


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._logger = logging.getLogger(__name__)
        self._dependency_graph: Dict[str, Set[str]] = {}
    
    def register_tool(self, tool_class: Type[BaseTool]) -> None:
        """注册工具"""
        tool = tool_class()
        metadata = tool.metadata
        
        # 检查工具名称是否已存在
        if metadata.name in self._tools:
            self._logger.warning(f"工具 {metadata.name} 已存在，将被覆盖")
        
        # 注册工具
        self._tools[metadata.name] = tool_class
        
        # 更新依赖图
        self._dependency_graph[metadata.name] = set(metadata.dependencies)
        
        self._logger.info(f"注册工具: {metadata.name} v{metadata.version}")
    
    def get_tool(self, name: str) -> Optional[Type[BaseTool]]:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolMetadata]:
        """列出所有工具"""
        return [tool().get_metadata() for tool in self._tools.values()]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """按类别获取工具"""
        return [
            tool().get_metadata()
            for tool in self._tools.values()
            if tool().get_metadata().category == category
        ]
    
    def check_dependencies(self, tool_name: str) -> bool:
        """检查工具依赖"""
        if tool_name not in self._dependency_graph:
            return False
        
        dependencies = self._dependency_graph[tool_name]
        return all(dep in self._tools for dep in dependencies)
    
    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """执行工具"""
        # 获取工具
        tool_class = self.get_tool(name)
        if not tool_class:
            return ToolResult(
                success=False,
                error=f"工具 {name} 不存在"
            )
        
        # 检查依赖
        if not self.check_dependencies(name):
            return ToolResult(
                success=False,
                error=f"工具 {name} 的依赖不满足"
            )
        
        # 创建工具实例
        tool = tool_class()
        
        # 验证参数
        if not tool.validate_params(**kwargs):
            return ToolResult(
                success=False,
                error=f"工具 {name} 的参数验证失败"
            )
        
        # 执行工具
        try:
            start_time = asyncio.get_event_loop().time()
            result = await asyncio.wait_for(
                tool.execute(**kwargs),
                timeout=tool.metadata.timeout
            )
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # 添加执行时间
            result.execution_time = execution_time
            
            return result
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error=f"工具 {name} 执行超时"
            )
        except Exception as e:
            self._logger.error(f"工具 {name} 执行失败: {str(e)}")
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    def get_tool_dependencies(self, name: str) -> Set[str]:
        """获取工具依赖"""
        return self._dependency_graph.get(name, set())
    
    def get_dependent_tools(self, name: str) -> Set[str]:
        """获取依赖此工具的工具"""
        return {
            tool_name
            for tool_name, deps in self._dependency_graph.items()
            if name in deps
        }


# 全局工具注册表实例
tool_registry = ToolRegistry() 