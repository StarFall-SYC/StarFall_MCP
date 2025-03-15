# StarFall MCP 开发指南

## 开发环境配置

### 1. 基础环境要求
- Python 3.10 或更高版本
- Git
- 编辑器（推荐 VS Code 或 PyCharm）
- Docker（可选，用于容器化部署）

### 2. 克隆项目
```bash
git clone https://github.com/StarFall/starfall-mcp.git
cd starfall-mcp
```

### 3. 虚拟环境设置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 4. 安装依赖
```bash
# 安装开发依赖（包含测试和文档工具）
pip install -e ".[dev]"

# 仅安装测试依赖
pip install -e ".[test]"

# 仅安装文档依赖
pip install -e ".[docs]"

# 安装生产环境依赖
pip install -r requirements.txt

# 安装预提交钩子
pre-commit install
```

### 5. IDE 配置

#### VS Code
1. 安装推荐扩展
   - Python
   - Pylance
   - Black Formatter
   - isort
   - GitLens

2. 配置 settings.json
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm
1. 启用 Black 格式化
   - 设置 > 工具 > 外部工具 > 添加 Black
   - 程序：`$PyInterpreterDirectory$/black`
   - 参数：`$FilePath$`

2. 配置 isort
   - 设置 > 工具 > 外部工具 > 添加 isort
   - 程序：`$PyInterpreterDirectory$/isort`
   - 参数：`$FilePath$`

### 5. 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置以下参数：
# - APP_NAME：应用名称
# - APP_VERSION：应用版本
# - DEBUG：调试模式（development/production）
# - DATABASE_URL：数据库连接字符串
# - REDIS_URL：Redis连接字符串
# - SECRET_KEY：应用密钥
```

## 项目结构说明

```
starfall-mcp/
├── api/                # API 接口模块
│   ├── auth.py        # 认证相关
│   ├── routes.py      # 路由定义
│   └── __init__.py    # 模块初始化
├── core/              # 核心功能模块
│   ├── config.py      # 配置管理
│   ├── security.py    # 安全框架
│   ├── tools.py       # 工具管理
│   ├── workflow.py    # 工作流管理
│   └── __init__.py    # 模块初始化
├── models/            # 数据模型
│   ├── base.py        # 基础模型
│   └── __init__.py    # 模块初始化
├── tools/             # 工具模块集合
│   ├── file_tools.py  # 文件操作工具
│   ├── system_tools.py # 系统工具
│   ├── code_tools.py  # 代码工具
│   ├── browser_tools.py # 浏览器工具
│   └── __init__.py    # 模块初始化
├── tests/             # 测试用例
│   ├── conftest.py    # 测试配置
│   ├── test_api.py    # API测试
│   ├── test_tools.py  # 工具测试
│   └── __init__.py    # 测试初始化
├── docs/              # 项目文档
├── scripts/           # 辅助脚本
├── .env.example      # 环境变量模板
├── setup.py          # 安装配置
└── README.md         # 项目说明
```

## 开发规范

### 1. 代码风格

#### Python 代码规范
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 行长度限制在 88 字符以内
- 使用类型注解

#### 代码格式化
```bash
# 格式化代码
black .

# 排序导入
isort .

# 代码质量检查
flake8

# 类型检查
mypy .
```

### 2. 提交规范

#### 分支管理
- main：主分支，保持稳定
- develop：开发分支
- feature/*：功能分支
- fix/*：修复分支
- release/*：发布分支

#### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型说明：
- feat：新功能
- fix：修复 Bug
- docs：文档更新
- style：代码格式（不影响代码运行的变动）
- refactor：重构（既不是新增功能，也不是修改 Bug 的代码变动）
- test：增加测试
- chore：构建过程或辅助工具的变动

### 3. 测试规范

#### 单元测试
- 使用 pytest 编写测试用例
- 测试文件命名：test_*.py
- 测试类命名：Test*
- 测试方法命名：test_*

#### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_tools.py

# 运行带覆盖率的测试
pytest --cov=starfall_mcp tests/

# 生成覆盖率报告
pytest --cov=starfall_mcp --cov-report=html tests/
```

## 调试指南

### 1. 本地调试
```bash
# 使用 uvicorn 启动服务（开发模式）
uvicorn main:app --reload --port 8000

# 使用 Python 调试器
python -m pdb main.py
```

### 2. 日志调试
- 日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 日志位置：logs/starfall.log
- 日志格式：时间 | 级别 | 模块 | 消息

### 3. API 调试
- 访问 Swagger 文档：http://localhost:8000/docs
- 访问 ReDoc 文档：http://localhost:8000/redoc
- 使用 Postman 或类似工具测试 API

## 常见问题

### 1. 依赖安装失败
- 检查 Python 版本是否满足要求
- 确保虚拟环境已激活
- 尝试更新 pip：pip install --upgrade pip

### 2. 测试失败
- 检查环境变量配置
- 确保数据库和 Redis 服务正常运行
- 查看测试日志获取详细错误信息

### 3. API 访问失败
- 检查服务是否正常运行
- 验证认证信息是否正确
- 查看服务日志定位问题

## 获取帮助

- 查看[常见问题文档](docs/faq.md)
- 提交 [Issue](https://github.com/StarFall/starfall-mcp/issues)
- 加入开发者社区获取支持