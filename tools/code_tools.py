"""
代码操作工具模块
"""
import ast
import re
from typing import Any, Dict, List, Optional

from ..core.tools import BaseTool, ToolCategory, ToolMetadata, ToolResult


class CodeAnalyzeTool(BaseTool):
    """代码分析工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_analyze",
            description="分析Python代码",
            category=ToolCategory.CODE,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "code": {"type": "string", "description": "Python代码"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            code = kwargs["code"]
            
            tree = ast.parse(code)
            
            imports = []
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        imports.append(f"{node.module}.{name.name}")
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [decorator.id for decorator in node.decorator_list if isinstance(decorator, ast.Name)]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                        "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                    })
            
            result = {
                "imports": imports,
                "functions": functions,
                "classes": classes
            }
            
            return ToolResult(
                success=True,
                output=str(result)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class CodeSearchTool(BaseTool):
    """代码搜索工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_search",
            description="搜索代码中的内容",
            category=ToolCategory.CODE,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "code": {"type": "string", "description": "Python代码"},
                "pattern": {"type": "string", "description": "搜索模式"},
                "case_sensitive": {"type": "boolean", "description": "是否区分大小写"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            code = kwargs["code"]
            pattern = kwargs["pattern"]
            case_sensitive = kwargs.get("case_sensitive", True)
            
            flags = 0 if case_sensitive else re.IGNORECASE
            matches = list(re.finditer(pattern, code, flags))
            
            results = []
            for match in matches:
                line_number = code.count("\n", 0, match.start()) + 1
                line_start = code.rfind("\n", 0, match.start()) + 1
                line_end = code.find("\n", match.end())
                if line_end == -1:
                    line_end = len(code)
                
                line = code[line_start:line_end].strip()
                results.append({
                    "line_number": line_number,
                    "line": line,
                    "start": match.start(),
                    "end": match.end(),
                    "match": match.group()
                })
            
            return ToolResult(
                success=True,
                output=str(results)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class CodeFormatTool(BaseTool):
    """代码格式化工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_format",
            description="格式化Python代码",
            category=ToolCategory.CODE,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=[],
            parameters={
                "code": {"type": "string", "description": "Python代码"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            code = kwargs["code"]
            
            # 解析代码
            tree = ast.parse(code)
            
            # 重新生成代码
            formatted_code = ast.unparse(tree)
            
            return ToolResult(
                success=True,
                output=formatted_code
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            ) 