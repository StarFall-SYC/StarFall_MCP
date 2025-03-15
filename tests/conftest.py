"""
测试配置文件
"""
import os
import pytest
from pathlib import Path
from typing import Generator, Dict, Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings
from ..core.security import security_manager
from ..core.tools import tool_registry
from ..core.workflow import workflow_manager
from ..api.main import app
from ..models.base import Base


@pytest.fixture(scope="session")
def test_settings() -> settings:
    """测试配置"""
    # 设置测试环境变量
    os.environ["ENV"] = "test"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["LOG_DIR"] = "test_logs"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    # 创建测试日志目录
    Path("test_logs").mkdir(exist_ok=True)
    
    return settings


@pytest.fixture(scope="session")
def test_db_engine(test_settings):
    """测试数据库引擎"""
    engine = create_engine(test_settings.get_database_url())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator:
    """测试数据库会话"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_client() -> Generator:
    """测试客户端"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def test_user() -> Dict[str, Any]:
    """测试用户"""
    return {
        "username": "test_user",
        "password": "test_password",
        "permissions": ["tool.execute", "tool.list", "workflow.create", "workflow.read"],
        "risk_level": "medium"
    }


@pytest.fixture(scope="function")
def test_token(test_user) -> str:
    """测试令牌"""
    return security_manager.create_token(test_user)


@pytest.fixture(scope="function")
def test_tool():
    """测试工具"""
    class TestTool:
        def get_metadata(self):
            return {
                "name": "test_tool",
                "description": "测试工具",
                "category": "test",
                "version": "1.0.0",
                "author": "test",
                "risk_level": "low",
                "parameters": {}
            }
        
        async def execute(self, **kwargs):
            return {
                "success": True,
                "output": "测试输出"
            }
    
    tool = TestTool()
    tool_registry.register_tool(tool)
    yield tool
    tool_registry.unregister_tool("test_tool")


@pytest.fixture(scope="function")
def test_workflow():
    """测试工作流"""
    workflow = workflow_manager.create_workflow(
        name="test_workflow",
        description="测试工作流",
        steps=[{
            "tool": "test_tool",
            "parameters": {}
        }]
    )
    yield workflow
    workflow_manager.delete_workflow(workflow.id)


@pytest.fixture(autouse=True)
def setup_test_env(test_settings):
    """设置测试环境"""
    yield
    
    # 清理测试日志目录
    if Path("test_logs").exists():
        for file in Path("test_logs").glob("*"):
            file.unlink()
        Path("test_logs").rmdir()
    
    # 清理测试数据库
    if Path("test.db").exists():
        Path("test.db").unlink() 