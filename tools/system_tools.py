"""
系统操作工具模块
"""
import os
import platform
import subprocess
from typing import Any, Dict, Optional

from ..core.tools import BaseTool, ToolCategory, ToolMetadata, ToolResult


class CommandExecuteTool(BaseTool):
    """命令执行工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="command_execute",
            description="执行系统命令",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="StarFall",
            risk_level="high",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "command": {"type": "string", "description": "要执行的命令"},
                "shell": {"type": "boolean", "description": "是否使用shell执行"},
                "timeout": {"type": "integer", "description": "超时时间(秒)"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            command = kwargs["command"]
            shell = kwargs.get("shell", False)
            timeout = kwargs.get("timeout", 30)
            
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    output=stdout
                )
            else:
                return ToolResult(
                    success=False,
                    error=stderr
                )
        except subprocess.TimeoutExpired:
            process.kill()
            return ToolResult(
                success=False,
                error="命令执行超时"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class SystemInfoTool(BaseTool):
    """系统信息工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="system_info",
            description="获取系统信息",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cwd": os.getcwd(),
                "env": dict(os.environ)
            }
            
            return ToolResult(
                success=True,
                output=str(info)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class ProcessListTool(BaseTool):
    """进程列表工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="process_list",
            description="列出系统进程",
            category=ToolCategory.SYSTEM,
            version="1.0.0",
            author="StarFall",
            risk_level="medium",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            if platform.system() == "Windows":
                command = "tasklist"
            else:
                command = "ps aux"
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    output=stdout
                )
            else:
                return ToolResult(
                    success=False,
                    error=stderr
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            ) 