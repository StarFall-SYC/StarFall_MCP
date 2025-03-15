"""
API路由模块
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.security import SecurityContext, security_manager
from ..core.tools import ToolRegistry, tool_registry
from ..core.workflow import Workflow, WorkflowManager, workflow_manager

router = APIRouter()


class ToolRequest(BaseModel):
    """工具请求模型"""
    name: str
    parameters: Dict[str, Any]


class WorkflowRequest(BaseModel):
    """工作流请求模型"""
    name: str
    description: Optional[str] = None
    steps: List[ToolRequest]


class WorkflowResponse(BaseModel):
    """工作流响应模型"""
    id: str
    name: str
    description: Optional[str]
    status: str
    steps: List[Dict[str, Any]]


async def get_security_context() -> SecurityContext:
    """获取安全上下文"""
    return security_manager.create_context()


async def get_tool_registry() -> ToolRegistry:
    """获取工具注册表"""
    return tool_registry


async def get_workflow_manager() -> WorkflowManager:
    """获取工作流管理器"""
    return workflow_manager


@router.post("/tools/execute", response_model=Dict[str, Any])
async def execute_tool(
    request: ToolRequest,
    security_context: SecurityContext = Depends(get_security_context),
    registry: ToolRegistry = Depends(get_tool_registry)
) -> Dict[str, Any]:
    """执行工具"""
    # 检查权限
    if not security_context.has_permission("tool.execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有执行工具的权限"
        )
    
    # 获取工具
    tool = registry.get_tool(request.name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具 {request.name} 不存在"
        )
    
    # 检查风险
    risk_level = security_manager.evaluate_risk(tool.get_metadata().risk_level)
    if risk_level > security_context.risk_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工具风险等级过高"
        )
    
    # 执行工具
    result = await tool.execute(**request.parameters)
    
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error
    }


@router.get("/tools", response_model=List[Dict[str, Any]])
async def list_tools(
    security_context: SecurityContext = Depends(get_security_context),
    registry: ToolRegistry = Depends(get_tool_registry)
) -> List[Dict[str, Any]]:
    """列出所有工具"""
    # 检查权限
    if not security_context.has_permission("tool.list"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有列出工具的权限"
        )
    
    # 获取工具列表
    tools = registry.list_tools()
    
    # 过滤高风险工具
    filtered_tools = []
    for tool in tools:
        metadata = tool.get_metadata()
        risk_level = security_manager.evaluate_risk(metadata.risk_level)
        if risk_level <= security_context.risk_level:
            filtered_tools.append({
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category,
                "version": metadata.version,
                "author": metadata.author,
                "risk_level": metadata.risk_level,
                "parameters": metadata.parameters
            })
    
    return filtered_tools


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    security_context: SecurityContext = Depends(get_security_context),
    manager: WorkflowManager = Depends(get_workflow_manager)
) -> WorkflowResponse:
    """创建工作流"""
    # 检查权限
    if not security_context.has_permission("workflow.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建工作流的权限"
        )
    
    # 创建工作流
    workflow = await manager.create_workflow(
        name=request.name,
        description=request.description,
        steps=request.steps
    )
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        steps=[{
            "tool": step.tool,
            "parameters": step.parameters,
            "status": step.status,
            "result": step.result,
            "error": step.error
        } for step in workflow.steps]
    )


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    security_context: SecurityContext = Depends(get_security_context),
    manager: WorkflowManager = Depends(get_workflow_manager)
) -> WorkflowResponse:
    """获取工作流"""
    # 检查权限
    if not security_context.has_permission("workflow.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有读取工作流的权限"
        )
    
    # 获取工作流
    workflow = await manager.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        steps=[{
            "tool": step.tool,
            "parameters": step.parameters,
            "status": step.status,
            "result": step.result,
            "error": step.error
        } for step in workflow.steps]
    )


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    security_context: SecurityContext = Depends(get_security_context),
    manager: WorkflowManager = Depends(get_workflow_manager)
) -> List[WorkflowResponse]:
    """列出所有工作流"""
    # 检查权限
    if not security_context.has_permission("workflow.list"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有列出工作流的权限"
        )
    
    # 获取工作流列表
    workflows = await manager.list_workflows()
    
    return [WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        steps=[{
            "tool": step.tool,
            "parameters": step.parameters,
            "status": step.status,
            "result": step.result,
            "error": step.error
        } for step in workflow.steps]
    ) for workflow in workflows]


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    security_context: SecurityContext = Depends(get_security_context),
    manager: WorkflowManager = Depends(get_workflow_manager)
) -> Dict[str, Any]:
    """删除工作流"""
    # 检查权限
    if not security_context.has_permission("workflow.delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除工作流的权限"
        )
    
    # 删除工作流
    success = await manager.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    return {"success": True} 