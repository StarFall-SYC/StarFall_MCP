#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
import platform
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('direct-deploy')

class DirectDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / '.env'
        self.venv_path = self.project_root / 'venv'
        self.is_windows = platform.system().lower() == 'windows'

    def check_system_dependencies(self):
        """检查系统依赖"""
        try:
            # 检查Python版本
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
                logger.error('Python版本必须是3.10或以上')
                return False

            # 检查PostgreSQL
            try:
                subprocess.run(['psql', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error('请确保PostgreSQL已正确安装')
                return False

            # 检查Redis
            try:
                subprocess.run(['redis-cli', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error('请确保Redis已正确安装')
                return False

            logger.info('系统依赖检查通过')
            return True
        except Exception as e:
            logger.error(f'系统依赖检查失败: {str(e)}')
            return False

    def setup_virtual_env(self):
        """设置Python虚拟环境"""
        try:
            if not self.venv_path.exists():
                logger.info('创建虚拟环境')
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)

            # 获取虚拟环境中的Python和pip路径
            if self.is_windows:
                python_path = self.venv_path / 'Scripts' / 'python.exe'
                pip_path = self.venv_path / 'Scripts' / 'pip.exe'
            else:
                python_path = self.venv_path / 'bin' / 'python'
                pip_path = self.venv_path / 'bin' / 'pip'

            # 安装依赖
            logger.info('安装项目依赖')
            subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], 
                          check=True, cwd=str(self.project_root))
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f'虚拟环境设置失败: {str(e)}')
            return False

    def prepare_env_file(self):
        """准备环境变量文件"""
        if not self.env_file.exists():
            env_example = self.project_root / '.env.example'
            if env_example.exists():
                logger.info('正在从.env.example创建.env文件')
                with open(env_example, 'r', encoding='utf-8') as src:
                    with open(self.env_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                logger.info('已创建.env文件，请根据需要修改配置')
            else:
                logger.error('未找到.env.example文件')
                return False
        return True

    def setup_database(self):
        """配置数据库"""
        try:
            # 创建数据库和用户的SQL命令
            create_db_sql = """
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'starfall') THEN
                    CREATE DATABASE starfall;
                END IF;
                IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'starfall') THEN
                    CREATE USER starfall WITH PASSWORD 'starfall';
                END IF;
                GRANT ALL PRIVILEGES ON DATABASE starfall TO starfall;
            END
            $$;
            """

            # 执行SQL命令
            logger.info('配置数据库')
            subprocess.run(['psql', '-U', 'postgres', '-c', create_db_sql], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f'数据库配置失败: {str(e)}')
            return False

    def start_service(self):
        """启动服务"""
        try:
            # 获取Python解释器路径
            if self.is_windows:
                python_path = self.venv_path / 'Scripts' / 'python.exe'
            else:
                python_path = self.venv_path / 'bin' / 'python'

            # 启动服务
            logger.info('启动StarFall MCP服务')
            cmd = [str(python_path), '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000']
            subprocess.Popen(cmd, cwd=str(self.project_root))
            
            logger.info('服务已启动！')
            return True
        except Exception as e:
            logger.error(f'服务启动失败: {str(e)}')
            return False

    def deploy(self):
        """执行完整的部署流程"""
        logger.info('开始StarFall MCP直接部署流程')

        if not self.check_system_dependencies():
            return False

        if not self.setup_virtual_env():
            return False

        if not self.prepare_env_file():
            return False

        if not self.setup_database():
            return False

        if not self.start_service():
            return False

        logger.info('StarFall MCP部署完成！')
        logger.info('访问 http://localhost:8000 查看服务是否正常运行')
        return True

def main():
    deployer = DirectDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()