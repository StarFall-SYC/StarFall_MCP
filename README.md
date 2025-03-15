<<<<<<< HEAD
# StarFall MCP

基于 MCP 协议的智能代理系统，实现自然语言到系统操作的安全转化。

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage](https://img.shields.io/badge/coverage-85%25-green.svg)](https://github.com/StarFall/starfall-mcp/actions)

## 功能特点

- **自然语言接口**：解析复杂指令为可执行工作流
- **跨平台兼容**：支持 Windows/macOS/Linux 系统操作
- **安全优先设计**：高危操作强制确认，实时威胁检测
- **原子化任务执行**：模块化系统操作为可审计工具
- **可扩展架构**：支持第三方 API 与自定义插件集成

## 系统要求

- Python 3.10+
- 操作系统：Windows/macOS/Linux
- 内存：4GB+
- 磁盘空间：1GB+

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/StarFall/starfall-mcp.git
cd starfall-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -e ".[dev]"  # 开发环境
# 或
pip install -e ".[test]"  # 测试环境
# 或
pip install -r requirements.txt  #使用依赖
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件设置必要的配置
```

### 3. 运行

```bash
# 启动服务
starfall run

# 或使用 Python 模块
python -m starfall_mcp.main
```

### 4. 访问 API

服务启动后，访问以下地址：
- API 文档：http://localhost:8000/docs
- 交互式文档：http://localhost:8000/redoc

## 开发指南

### 项目结构

```
starfall-mcp/
├── api/                # API 接口
├── core/              # 核心功能
├── models/            # 数据模型
├── tools/             # 工具模块
├── tests/             # 测试用例
├── docs/              # 文档
├── scripts/           # 脚本
├── .env.example       # 环境变量模板
├── setup.py           # 安装配置
└── README.md          # 项目说明
```

### 开发流程

1. **代码风格**
   ```bash
   # 格式化代码
   black .
   isort .
   
   # 类型检查
   mypy .
   
   # 代码检查
   flake8
   ```

2. **测试**
   ```bash
   # 运行测试
   pytest
   
   # 生成覆盖率报告
   pytest --cov=starfall_mcp --cov-report=html
   ```

3. **文档**
   ```bash
   # 生成文档
   mkdocs build
   
   # 预览文档
   mkdocs serve
   ```

### 添加新工具

1. 在 `tools/` 目录下创建新的工具模块
2. 继承 `BaseTool` 类并实现必要的方法
3. 在 `tools/__init__.py` 中注册工具
4. 添加相应的测试用例

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t starfall-mcp .

# 运行容器
docker run -d -p 8000:8000 starfall-mcp
```

### 系统服务部署

1. 创建系统服务文件 `/etc/systemd/system/starfall-mcp.service`
2. 配置服务
3. 启动服务
   ```bash
   sudo systemctl enable starfall-mcp
   sudo systemctl start starfall-mcp
   ```

## 安全说明

- 所有工具执行前进行风险评估
- 高危操作需要用户确认
- 支持细粒度的权限控制
- 详细的审计日志记录

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 作者：StarFall
- 邮箱：SYC_Hello@163.com
- 项目主页：https://github.com/StarFall/starfall-mcp

## 致谢

感谢所有为本项目做出贡献的开发者！ 
=======
