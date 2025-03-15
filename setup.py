"""
项目安装配置文件
"""
from setuptools import setup, find_packages


setup(
    name="starfall-mcp",
    version="0.1.0",
    description="基于 MCP 协议的智能代理系统",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="StarFall",
    author_email="SYC_Hello@163.com",
    url="https://github.com/StarFall/starfall-mcp",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        # Web框架
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        
        # 数据库
        "sqlalchemy>=2.0.0",
        "alembic>=1.11.0",
        "aiosqlite>=0.19.0",
        
        # 安全
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        
        # 工具
        "selenium>=4.10.0",
        "psutil>=5.9.0",
        "watchdog>=3.0.0",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.12.0",
        "black>=23.7.0",
        "isort>=5.12.0",
        "mypy>=1.5.1",
        
        # 日志
        "structlog>=23.1.0",
        "colorama>=0.4.6",
        
        # 缓存
        "redis>=5.0.0",
        "aioredis>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "pytest-xdist>=3.3.0",
            "coverage>=7.3.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.1",
            "flake8>=6.1.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.2.0",
            "mkdocstrings>=0.18.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "pytest-xdist>=3.3.0",
            "coverage>=7.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "starfall=starfall_mcp.cli:main",
            "starfall-migrate=starfall_mcp.cli:migrate",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: FastAPI",
        "Typing :: Typed",
    ],
    keywords=[
        "mcp",
        "ai",
        "agent",
        "automation",
        "workflow",
        "tools",
        "fastapi",
    ],
) 