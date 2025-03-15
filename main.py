"""
主程序
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.config import settings
from core.security import security_manager
from core.tools import tool_registry
from core.workflow import workflow_manager
from tools import (
    BrowserExtractTool,
    BrowserOpenTool,
    BrowserScreenshotTool,
    CodeAnalyzeTool,
    CodeFormatTool,
    CodeSearchTool,
    CommandExecuteTool,
    DirectoryListTool,
    FileCreateTool,
    FileDeleteTool,
    FileReadTool,
    ProcessListTool,
    SystemInfoTool
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_DIR / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="StarFall MCP",
    description="基于MCP协议的智能代理系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from api import router as api_router
app.include_router(api_router, prefix="/api/v1")


class ToolRequest(BaseModel):
    """工具请求模型"""
    name: str
    parameters: Dict[str, Any]


class WorkflowRequest(BaseModel):
    """工作流请求模型"""
    name: str
    description: Optional[str] = None
    steps: List[ToolRequest]


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("正在启动StarFall MCP...")
    
    # 注册工具
    tools = [
        # 文件操作工具
        FileCreateTool(),
        FileReadTool(),
        FileDeleteTool(),
        DirectoryListTool(),
        
        # 系统操作工具
        CommandExecuteTool(),
        SystemInfoTool(),
        ProcessListTool(),
        
        # 代码操作工具
        CodeAnalyzeTool(),
        CodeSearchTool(),
        CodeFormatTool(),
        
        # 浏览器操作工具
        BrowserOpenTool(),
        BrowserScreenshotTool(),
        BrowserExtractTool()
    ]
    
    for tool in tools:
        tool_registry.register_tool(tool)
    
    logger.info(f"已注册 {len(tools)} 个工具")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("正在关闭StarFall MCP...")


@app.get("/")
async def root() -> Dict[str, Any]:
    """根路径"""
    return {
        "name": "StarFall MCP",
        "version": "1.0.0",
        "description": "基于MCP协议的智能代理系统"
    }


@app.post("/token")
async def login(username: str, password: str) -> Dict[str, Any]:
    """登录"""
    # 验证用户
    user = security_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建令牌
    access_token = security_manager.create_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/tools/execute")
async def execute_tool(request: ToolRequest) -> Dict[str, Any]:
    """执行工具"""
    # 获取工具
    tool = tool_registry.get_tool(request.name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具 {request.name} 不存在"
        )
    
    # 执行工具
    result = await tool.execute(**request.parameters)
    
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error
    }


@app.get("/tools")
async def list_tools() -> List[Dict[str, Any]]:
    """列出所有工具"""
    tools = tool_registry.list_tools()
    return [{
        "name": tool.get_metadata().name,
        "description": tool.get_metadata().description,
        "category": tool.get_metadata().category,
        "version": tool.get_metadata().version,
        "author": tool.get_metadata().author,
        "risk_level": tool.get_metadata().risk_level,
        "parameters": tool.get_metadata().parameters
    } for tool in tools]


@app.post("/workflows")
async def create_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """创建工作流"""
    # 创建工作流
    workflow = await workflow_manager.create_workflow(
        name=request.name,
        description=request.description,
        steps=request.steps
    )
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status,
        "steps": [{
            "tool": step.tool,
            "parameters": step.parameters,
            "status": step.status,
            "result": step.result,
            "error": step.error
        } for step in workflow.steps]
    }


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """获取工作流"""
    # 获取工作流
    workflow = await workflow_manager.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status,
        "steps": [{
            "tool": step.tool,
            "parameters": step.parameters,
            "status": step.status,
            "result": step.result,
            "error": step.error
        } for step in workflow.steps]
    }


@app.get("/workflows")
async def list_workflows() -> List[Dict[str, Any]]:
    """列出所有工作流"""
    workflows = await workflow_manager.list_workflows()
    return [{
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status,
        "steps": [{
            "tool": step.tool,
            "parameters": step.parameters,
            "status": step.status,
            "result": step.result,
            "error": step.error
        } for step in workflow.steps]
    } for workflow in workflows]


@app.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str) -> Dict[str, Any]:
    """删除工作流"""
    # 删除工作流
    success = await workflow_manager.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 