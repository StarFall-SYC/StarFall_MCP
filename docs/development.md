# StarFall MCP 开发指南

## 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/StarFall/starfall-mcp.git
cd starfall-mcp
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装测试依赖
pip install -e ".[test]"

# 安装文档依赖
pip install -e ".[docs]"
```

### 4. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件设置必要的配置
```

## 项目结构

```
starfall-mcp/
├── api/                # API 接口
│   ├── auth.py        # 认证相关
│   ├── routes.py      # 路由定义
│   └── __init__.py    # 包初始化
├── core/              # 核心功能
│   ├── config.py      # 配置管理
│   ├── security.py    # 安全框架
│   ├── tools.py       # 工具管理
│   ├── workflow.py    # 工作流管理
│   └── __init__.py    # 包初始化
├── models/            # 数据模型
│   ├── base.py        # 基础模型
│   └── __init__.py    # 包初始化
├── tools/             # 工具模块
│   ├── file_tools.py  # 文件工具
│   ├── system_tools.py # 系统工具
│   ├── code_tools.py  # 代码工具
│   ├── browser_tools.py # 浏览器工具
│   └── __init__.py    # 包初始化
├── tests/             # 测试用例
│   ├── conftest.py    # 测试配置
│   ├── test_api.py    # API测试
│   ├── test_tools.py  # 工具测试
│   └── __init__.py    # 包初始化
├── docs/              # 文档
│   ├── api.md         # API文档
│   ├── development.md # 开发指南
│   ├── deployment.md  # 部署指南
│   └── contributing.md # 贡献指南
├── scripts/           # 脚本
├── .env.example       # 环境变量模板
├── setup.py           # 安装配置
└── README.md          # 项目说明
```

## 开发标准

### 1. 代码风格
- 使用 Black 格式化代码
- 使用 isort 排序导入
- 使用 flake8 检查代码质量
- 使用 mypy 进行类型检查

### 2. 提交规范
```bash
# 提交信息格式
<type>(<scope>): <subject>

<body>

<footer>
```

类型说明：
- feat: 新功能
- fix: 修复 Bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

### 3. 分支管理
- main: 主分支，保持稳定
- develop: 开发分支
- feature/*: 功能分支
- fix/*: 修复分支
- release/*: 发布分支

## 测试

### 1. 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_tools.py

# 运行带覆盖率报告的测试
pytest --cov=starfall_mcp tests/
```

### 2. 编写测试
```python
def test_tool_execution():
    """测试工具执行"""
    # 准备测试数据
    tool_name = "file_create"
    params = {
        "path": "test.txt",
        "content": "test content"
    }

    # 执行测试
    result = execute_tool(tool_name, params)

    # 验证结果
    assert result["status"] == "success"
    assert os.path.exists("test.txt")
```

## 文档

### 1. 生成文档
```bash
# 生成 API 文档
sphinx-build -b html docs/source docs/build

# 生成类型提示文档
mypy starfall_mcp --html-report docs/type_report
```

### 2. 编写文档
- 使用 Markdown 格式
- 添加代码示例
- 包含使用说明
- 更新变更日志

## 调试

### 1. 日志调试
```python
import logging

logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
```

### 2. 断点调试
```python
import pdb

def complex_function():
    # 设置断点
    pdb.set_trace()
    
    # 代码执行
    result = process_data()
    
    return result
```

## 性能优化

### 1. 代码优化
- 使用性能分析工具
- 优化算法复杂度
- 减少内存使用
- 提高并发性能

### 2. 资源管理
- 及时释放资源
- 使用连接池
- 实现缓存机制
- 优化数据库查询

## 安全

### 1. 代码安全
- 输入验证
- 输出转义
- 权限控制
- 敏感信息保护

### 2. 运行时安全
- 异常处理
- 日志记录
- 访问控制
- 数据加密

## 发布流程

### 1. 版本管理
```bash
# 创建发布分支
git checkout -b release/v1.0.0

# 更新版本号
bumpversion patch  # 小版本更新
bumpversion minor  # 中版本更新
bumpversion major  # 大版本更新

# 合并到主分支
git checkout main
git merge release/v1.0.0
```

### 2. 打包发布
```bash
# 构建包
python setup.py sdist bdist_wheel

# 发布到 PyPI
twine upload dist/*
```

## 常见问题

### 1. 依赖安装失败
- 检查 Python 版本
- 更新 pip
- 清理缓存
- 使用镜像源

### 2. 测试失败
- 检查测试环境
- 更新测试数据
- 修复测试用例
- 检查依赖版本

### 3. 文档生成失败
- 检查 Sphinx 配置
- 修复文档格式
- 更新依赖版本
- 清理构建目录

## 联系方式

- 作者：StarFall
- 邮箱：SYC_Hello@163.com
- 项目主页：https://github.com/StarFall/starfall-mcp 