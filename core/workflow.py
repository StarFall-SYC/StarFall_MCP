"""
工作流管理模块
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    """工作流步骤"""
    tool_name: str
    parameters: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    rollback_data: Optional[Dict[str, Any]] = None


class Workflow(BaseModel):
    """工作流"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        self._logger = logging.getLogger(__name__)
        self._data_dir = Path("data/workflows")
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._load_workflows()
    
    def _load_workflows(self):
        """加载工作流"""
        for file in self._data_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    workflow = Workflow(**data)
                    self._workflows[workflow.id] = workflow
                    self._logger.info(f"加载工作流: {workflow.id}")
            except Exception as e:
                self._logger.error(f"加载工作流失败 {file}: {str(e)}")
    
    def _save_workflow(self, workflow: Workflow):
        """保存工作流"""
        try:
            file = self._data_dir / f"{workflow.id}.json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(workflow.dict(), f, ensure_ascii=False, indent=2)
            self._logger.info(f"保存工作流: {workflow.id}")
        except Exception as e:
            self._logger.error(f"保存工作流失败 {workflow.id}: {str(e)}")
    
    def create_workflow(self, name: str, description: str, steps: List[WorkflowStep]) -> Workflow:
        """创建工作流"""
        workflow = Workflow(
            id=f"wf_{len(self._workflows) + 1}",
            name=name,
            description=description,
            steps=steps
        )
        self._workflows[workflow.id] = workflow
        self._save_workflow(workflow)
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        return self._workflows.get(workflow_id)
    
    def update_workflow_status(self, workflow_id: str, status: str) -> None:
        """更新工作流状态"""
        if workflow := self._workflows.get(workflow_id):
            workflow.status = status
            workflow.updated_at = datetime.now()
            self._save_workflow(workflow)
    
    def update_step_status(
        self,
        workflow_id: str,
        step_index: int,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        rollback_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """更新步骤状态"""
        if workflow := self._workflows.get(workflow_id):
            if 0 <= step_index < len(workflow.steps):
                step = workflow.steps[step_index]
                step.status = status
                if status == "running":
                    step.start_time = datetime.now()
                elif status in ["completed", "failed"]:
                    step.end_time = datetime.now()
                if result is not None:
                    step.result = result
                if error is not None:
                    step.error = error
                if rollback_data is not None:
                    step.rollback_data = rollback_data
                
                # 记录历史
                workflow.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "step_index": step_index,
                    "status": status,
                    "result": result,
                    "error": error
                })
                
                workflow.updated_at = datetime.now()
                self._save_workflow(workflow)
    
    def list_workflows(self) -> List[Workflow]:
        """列出所有工作流"""
        return list(self._workflows.values())
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """删除工作流"""
        if workflow_id in self._workflows:
            file = self._data_dir / f"{workflow_id}.json"
            if file.exists():
                file.unlink()
            del self._workflows[workflow_id]
            return True
        return False
    
    def rollback_workflow(self, workflow_id: str, step_index: int) -> bool:
        """回滚工作流到指定步骤"""
        if workflow := self._workflows.get(workflow_id):
            if 0 <= step_index < len(workflow.steps):
                # 获取回滚数据
                step = workflow.steps[step_index]
                if not step.rollback_data:
                    return False
                
                # 执行回滚
                try:
                    # TODO: 实现具体的回滚逻辑
                    # 这里需要根据不同的工具类型实现不同的回滚策略
                    pass
                except Exception as e:
                    self._logger.error(f"回滚工作流失败 {workflow_id}: {str(e)}")
                    return False
                
                # 更新状态
                workflow.status = "rolled_back"
                workflow.updated_at = datetime.now()
                self._save_workflow(workflow)
                return True
        return False
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """获取工作流历史记录"""
        if workflow := self._workflows.get(workflow_id):
            return workflow.history
        return []


# 全局工作流管理器实例
workflow_manager = WorkflowManager() 