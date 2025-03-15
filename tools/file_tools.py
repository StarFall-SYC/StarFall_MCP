"""
文件操作工具模块
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.tools import BaseTool, ToolCategory, ToolMetadata, ToolResult


class FileCreateTool(BaseTool):
    """文件创建工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_create",
            description="创建新文件",
            category=ToolCategory.FILE,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "文件内容"},
                "overwrite": {"type": "boolean", "description": "是否覆盖已存在的文件"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            path = Path(kwargs["path"])
            content = kwargs.get("content", "")
            overwrite = kwargs.get("overwrite", False)
            
            if path.exists() and not overwrite:
                return ToolResult(
                    success=False,
                    error=f"文件 {path} 已存在"
                )
            
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            
            return ToolResult(
                success=True,
                output=f"文件 {path} 创建成功"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class FileReadTool(BaseTool):
    """文件读取工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_read",
            description="读取文件内容",
            category=ToolCategory.FILE,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "path": {"type": "string", "description": "文件路径"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            path = Path(kwargs["path"])
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"文件 {path} 不存在"
                )
            
            content = path.read_text()
            
            return ToolResult(
                success=True,
                output=content
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class FileDeleteTool(BaseTool):
    """文件删除工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_delete",
            description="删除文件",
            category=ToolCategory.FILE,
            version="1.0.0",
            author="StarFall",
            risk_level="medium",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "path": {"type": "string", "description": "文件路径"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            path = Path(kwargs["path"])
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"文件 {path} 不存在"
                )
            
            path.unlink()
            
            return ToolResult(
                success=True,
                output=f"文件 {path} 删除成功"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class DirectoryListTool(BaseTool):
    """目录列表工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="directory_list",
            description="列出目录内容",
            category=ToolCategory.FILE,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "path": {"type": "string", "description": "目录路径"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            path = Path(kwargs["path"])
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"目录 {path} 不存在"
                )
            
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"{path} 不是目录"
                )
            
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return ToolResult(
                success=True,
                output=str(items)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            ) 