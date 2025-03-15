"""
API测试模块
"""
import pytest
from fastapi.testclient import TestClient
from typing import Any, Dict

from api.main import app


client = TestClient(app)


def test_login():
    """测试登录"""
    response = client.post(
        "/token",
        data={
            "username": "test_user",
            "password": "test_password"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_list_tools():
    """测试列出工具"""
    # 获取访问令牌
    response = client.post(
        "/token",
        data={
            "username": "test_user",
            "password": "test_password"
        }
    )
    token = response.json()["access_token"]
    
    # 测试列出所有工具
    response = client.get(
        "/tools",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    
    # 测试按类别列出工具
    response = client.get(
        "/tools/file",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert all(tool["category"] == "file" for tool in tools)


def test_execute_command():
    """测试执行命令"""
    # 获取访问令牌
    response = client.post(
        "/token",
        data={
            "username": "test_user",
            "password": "test_password"
        }
    )
    token = response.json()["access_token"]
    
    # 测试执行简单命令
    response = client.post(
        "/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "text": "创建一个名为 test.txt 的文件",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "workflow_id" in result
    assert "results" in result


def test_workflow_operations():
    """测试工作流操作"""
    # 获取访问令牌
    response = client.post(
        "/token",
        data={
            "username": "test_user",
            "password": "test_password"
        }
    )
    token = response.json()["access_token"]
    
    # 创建工作流
    workflow_data = {
        "name": "Test Workflow",
        "description": "Test workflow description",
        "steps": [
            {
                "tool_name": "file_create",
                "parameters": {
                    "path": "test.txt",
                    "content": "Hello, World!"
                }
            }
        ]
    }
    
    response = client.post(
        "/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json=workflow_data
    )
    assert response.status_code == 200
    workflow = response.json()
    workflow_id = workflow["id"]
    
    # 获取工作流列表
    response = client.get(
        "/workflows",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workflows = response.json()
    assert any(w["id"] == workflow_id for w in workflows)
    
    # 获取工作流详情
    response = client.get(
        f"/workflows/{workflow_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workflow = response.json()
    assert workflow["id"] == workflow_id
    
    # 删除工作流
    response = client.delete(
        f"/workflows/{workflow_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 验证工作流已删除
    response = client.get(
        f"/workflows/{workflow_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 