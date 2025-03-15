"""开发工具模块"""
import ast
import json
import re
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright
from ..core.tools import BaseTool, ToolCategory, ToolMetadata, ToolResult


class BrowserOpenTool(BaseTool):
    """浏览器打开工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="browser_open",
            description="打开浏览器",
            category=ToolCategory.BROWSER,
            version="1.0.0",
            author="StarFall",
            risk_level="medium",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=["playwright"],
            parameters={
                "url": {"type": "string", "description": "要访问的URL"},
                "headless": {"type": "boolean", "description": "是否使用无头模式"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            url = kwargs["url"]
            headless = kwargs.get("headless", True)
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)
                page = await browser.new_page()
                
                await page.goto(url)
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle")
                
                # 获取页面信息
                title = await page.title()
                url = page.url
                
                await browser.close()
                
                return ToolResult(
                    success=True,
                    output=json.dumps({
                        "title": title,
                        "url": url
                    })
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class BrowserScreenshotTool(BaseTool):
    """浏览器截图工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="browser_screenshot",
            description="截取网页截图",
            category=ToolCategory.BROWSER,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=["playwright"],
            parameters={
                "url": {"type": "string", "description": "要截图的URL"},
                "path": {"type": "string", "description": "截图保存路径"},
                "full_page": {"type": "boolean", "description": "是否截取完整页面"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            url = kwargs["url"]
            path = kwargs["path"]
            full_page = kwargs.get("full_page", False)
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                await page.goto(url)
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle")
                
                # 截取截图
                await page.screenshot(path=path, full_page=full_page)
                
                await browser.close()
                
                return ToolResult(
                    success=True,
                    output=f"截图已保存到 {path}"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class BrowserExtractTool(BaseTool):
    """浏览器内容提取工具"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="browser_extract",
            description="提取网页内容",
            category=ToolCategory.BROWSER,
            version="1.0.0",
            author="StarFall",
            risk_level="low",
            os_compatibility=["windows", "linux", "macos"],
            dependencies=["playwright"],
            parameters={
                "url": {"type": "string", "description": "要提取内容的URL"},
                "selector": {"type": "string", "description": "CSS选择器"}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            url = kwargs["url"]
            selector = kwargs["selector"]
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                await page.goto(url)
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle")
                
                # 提取内容
                elements = await page.query_selector_all(selector)
                
                results = []
                for element in elements:
                    text = await element.text_content()
                    results.append(text.strip())
                
                await browser.close()
                
                return ToolResult(
                    success=True,
                    output=json.dumps(results)
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


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
            matches = re.finditer(pattern, code, flags=flags)
            
            results = []
            for match in matches:
                start, end = match.span()
                line_start = code.count("\n", 0, start) + 1
                line_end = code.count("\n", 0, end) + 1
                
                results.append({
                    "match": match.group(),
                    "start": start,
                    "end": end,
                    "line_start": line_start,
                    "line_end": line_end
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