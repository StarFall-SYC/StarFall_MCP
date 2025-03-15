"""
浏览器操作工具模块
"""
import json
from typing import Any, Dict, Optional

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