"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""
    
    def __init__(self, settings: 'Settings'):
        self.settings = settings
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.src_path.endswith('.env'):
            self.settings.reload()


class Settings(BaseSettings):
    """系统配置"""
    
    # 应用配置
    APP_NAME: str = Field(default="StarFall MCP", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    
    # 基础配置
    DEBUG: bool = Field(default=False, description="调试模式")
    ENVIRONMENT: str = Field(default="production", description="运行环境")
    WORKERS: int = Field(default=4, description="工作进程数")
    RELOAD: bool = Field(default=False, description="热重载")
    
    # 安全配置
    SECRET_KEY: str = Field(default="!9gg4f$e8^l&kq3mz2#x@d5%v7j0bn1p", min_length=32, description="加密密钥")
    
    # 安全配置
    SECRET_KEY: str = Field(..., description="加密密钥")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间")
    
    # 服务配置
    HOST: str = Field(default="0.0.0.0", description="服务主机")
    PORT: int = Field(default=8000, description="服务端口")
    
    # 路径配置
    BASE_DIR: Path = Field(default=Path(__file__).parent.parent)
    LOG_DIR: Path = Field(default=Path("logs"))
    
    # 工具配置
    MAX_CONCURRENT_TOOLS: int = Field(default=5, description="最大并发工具数")
    TOOL_TIMEOUT: int = Field(default=30, description="工具执行超时时间(秒)")
    
    # 风险评估配置
    RISK_THRESHOLD: float = Field(default=0.7, description="风险阈值")
    
    # 缓存配置
    CACHE_ENABLED: bool = Field(default=True, description="是否启用缓存")
    CACHE_TTL: int = Field(default=300, description="缓存过期时间(秒)")
    
    # 数据库配置
    DATABASE_URL: Optional[str] = Field(default=None, description="数据库连接URL")
    DATABASE_POOL_SIZE: int = Field(default=5, description="数据库连接池大小")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="最大溢出连接数")
    
    # Redis配置
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    REDIS_POOL_SIZE: int = Field(default=5, description="Redis连接池大小")
    
    # JWT配置
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    JWT_EXPIRATION: int = Field(default=3600, description="JWT过期时间(秒)")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="日志格式")
    
    # 监控配置
    PROMETHEUS_ENABLED: bool = Field(default=True, description="启用Prometheus监控")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus端口")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """验证密钥长度"""
        if len(v) < 32:
            raise ValueError('密钥长度必须大于32位')
        return v
    
    @validator('PORT')
    def validate_port(cls, v):
        """验证端口范围"""
        if not 1 <= v <= 65535:
            raise ValueError('端口必须在1-65535之间')
        return v
    
    @validator('MAX_CONCURRENT_TOOLS')
    def validate_max_tools(cls, v):
        """验证最大并发工具数"""
        if v < 1:
            raise ValueError('最大并发工具数必须大于0')
        return v
    
    @validator('RISK_THRESHOLD')
    def validate_risk_threshold(cls, v):
        """验证风险阈值"""
        if not 0 <= v <= 1:
            raise ValueError('风险阈值必须在0-1之间')
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_file_watcher()
    
    def _setup_file_watcher(self):
        """设置配置文件监控"""
        if self.DEBUG:
            event_handler = ConfigFileHandler(self)
            observer = Observer()
            observer.schedule(event_handler, path=str(self.BASE_DIR), recursive=False)
            observer.start()
    
    def reload(self):
        """重新加载配置"""
        self.__init__()
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"sqlite:///{self.BASE_DIR}/data/database.db"


# 全局配置实例
settings = Settings()