"""
工具测试模块
"""
import os
import pytest
from pathlib import Path
from typing import Any, Dict

from tools.file_tools import (
    FileCreateTool,
    FileReadTool,
    FileDeleteTool,
    DirectoryListTool
)
from tools.system_tools import (
    ProcessListTool,
    SystemInfoTool,
    CommandExecuteTool
)
from tools.code_tools import (
    ProjectInitTool,
    PackageInstallTool,
    BuildTool
)


@pytest.fixture
def temp_dir(tmp_path):
    """临时目录"""
    return tmp_path


@pytest.mark.asyncio
async def test_file_create_tool(temp_dir):
    """测试文件创建工具"""
    tool = FileCreateTool()
    
    # 测试创建文件
    result = await tool.execute(
        path=str(temp_dir / "test.txt"),
        content="Hello, World!"
    )
    assert result.success
    assert (temp_dir / "test.txt").exists()
    
    # 测试文件内容
    content = (temp_dir / "test.txt").read_text()
    assert content == "Hello, World!"
    
    # 测试覆盖已存在的文件
    result = await tool.execute(
        path=str(temp_dir / "test.txt"),
        content="New content",
        overwrite=True
    )
    assert result.success
    content = (temp_dir / "test.txt").read_text()
    assert content == "New content"


@pytest.mark.asyncio
async def test_file_read_tool(temp_dir):
    """测试文件读取工具"""
    tool = FileReadTool()
    
    # 创建测试文件
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, World!")
    
    # 测试读取文件
    result = await tool.execute(path=str(test_file))
    assert result.success
    assert result.output == "Hello, World!"
    
    # 测试读取不存在的文件
    result = await tool.execute(path=str(temp_dir / "nonexistent.txt"))
    assert not result.success


@pytest.mark.asyncio
async def test_file_delete_tool(temp_dir):
    """测试文件删除工具"""
    tool = FileDeleteTool()
    
    # 创建测试文件
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, World!")
    
    # 测试删除文件
    result = await tool.execute(path=str(test_file))
    assert result.success
    assert not test_file.exists()
    
    # 测试删除不存在的文件
    result = await tool.execute(path=str(temp_dir / "nonexistent.txt"))
    assert not result.success


@pytest.mark.asyncio
async def test_directory_list_tool(temp_dir):
    """测试目录列表工具"""
    tool = DirectoryListTool()
    
    # 创建测试文件和目录
    (temp_dir / "file1.txt").write_text("File 1")
    (temp_dir / "file2.txt").write_text("File 2")
    (temp_dir / "dir1").mkdir()
    (temp_dir / "dir2").mkdir()
    
    # 测试列出目录内容
    result = await tool.execute(path=str(temp_dir))
    assert result.success
    
    # 验证结果
    items = eval(result.output)
    assert len(items) == 4
    assert any(item["name"] == "file1.txt" and item["type"] == "file" for item in items)
    assert any(item["name"] == "file2.txt" and item["type"] == "file" for item in items)
    assert any(item["name"] == "dir1" and item["type"] == "directory" for item in items)
    assert any(item["name"] == "dir2" and item["type"] == "directory" for item in items)


@pytest.mark.asyncio
async def test_process_list_tool():
    """测试进程列表工具"""
    tool = ProcessListTool()
    
    # 测试列出所有进程
    result = await tool.execute()
    assert result.success
    
    # 测试过滤进程
    result = await tool.execute(filter="python")
    assert result.success


@pytest.mark.asyncio
async def test_system_info_tool():
    """测试系统信息工具"""
    tool = SystemInfoTool()
    
    # 测试获取系统信息
    result = await tool.execute()
    assert result.success
    
    # 验证结果
    info = eval(result.output)
    assert "os" in info
    assert "os_version" in info
    assert "cpu_count" in info
    assert "memory_total" in info
    assert "memory_available" in info
    assert "disk_partitions" in info


@pytest.mark.asyncio
async def test_command_execute_tool():
    """测试命令执行工具"""
    tool = CommandExecuteTool()
    
    # 测试执行简单命令
    result = await tool.execute(command="echo Hello, World!")
    assert result.success
    assert result.output.strip() == "Hello, World!"
    
    # 测试执行危险命令
    result = await tool.execute(command="rm -rf /")
    assert not result.success
    assert "危险命令已被阻止" in result.error


@pytest.mark.asyncio
async def test_project_init_tool(temp_dir):
    """测试项目初始化工具"""
    tool = ProjectInitTool()
    
    # 测试初始化 Python 项目
    result = await tool.execute(
        name="test_python",
        type="python",
        path=str(temp_dir / "python_project")
    )
    assert result.success
    
    project_dir = temp_dir / "python_project"
    assert (project_dir / "src").exists()
    assert (project_dir / "tests").exists()
    assert (project_dir / "requirements.txt").exists()
    assert (project_dir / "README.md").exists()
    
    # 测试初始化 Node.js 项目
    result = await tool.execute(
        name="test_nodejs",
        type="nodejs",
        path=str(temp_dir / "nodejs_project")
    )
    assert result.success
    
    project_dir = temp_dir / "nodejs_project"
    assert (project_dir / "src").exists()
    assert (project_dir / "tests").exists()
    assert (project_dir / "package.json").exists()
    
    # 测试初始化 Java 项目
    result = await tool.execute(
        name="test_java",
        type="java",
        path=str(temp_dir / "java_project")
    )
    assert result.success
    
    project_dir = temp_dir / "java_project"
    assert (project_dir / "src" / "main" / "java").exists()
    assert (project_dir / "src" / "test" / "java").exists()
    assert (project_dir / "pom.xml").exists()


@pytest.mark.asyncio
async def test_package_install_tool(temp_dir):
    """测试包安装工具"""
    tool = PackageInstallTool()
    
    # 创建测试项目
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    (project_dir / "requirements.txt").write_text("pytest==7.4.0\n")
    
    # 测试安装 Python 包
    result = await tool.execute(
        path=str(project_dir),
        type="python"
    )
    assert result.success


@pytest.mark.asyncio
async def test_build_tool(temp_dir):
    """测试构建工具"""
    tool = BuildTool()
    
    # 创建测试项目
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # 测试构建 Python 项目
    result = await tool.execute(
        path=str(project_dir),
        type="python"
    )
    assert result.success 