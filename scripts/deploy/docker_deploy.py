#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docker-deploy')

class DockerDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / '.env'
        self.docker_compose_file = self.project_root / 'docker-compose.yml'

    def check_docker(self):
        """检查Docker和Docker Compose是否已安装"""
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            logger.info('Docker环境检查通过')
            return True
        except subprocess.CalledProcessError:
            logger.error('请确保Docker和Docker Compose已正确安装')
            return False
        except FileNotFoundError:
            logger.error('未找到Docker或Docker Compose命令')
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

    def build_and_start(self):
        """构建和启动Docker服务"""
        try:
            logger.info('开始构建Docker镜像')
            subprocess.run(['docker-compose', 'build'], check=True, cwd=str(self.project_root))
            
            logger.info('启动Docker服务')
            subprocess.run(['docker-compose', 'up', '-d'], check=True, cwd=str(self.project_root))
            
            logger.info('检查服务状态')
            subprocess.run(['docker-compose', 'ps'], check=True, cwd=str(self.project_root))
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f'Docker部署失败: {str(e)}')
            return False

    def deploy(self):
        """执行完整的部署流程"""
        logger.info('开始StarFall MCP Docker部署流程')
        
        if not self.check_docker():
            return False
        
        if not self.prepare_env_file():
            return False
        
        if not self.build_and_start():
            return False
        
        logger.info('StarFall MCP部署完成！')
        logger.info('访问 http://localhost:8000 查看服务是否正常运行')
        return True

def main():
    deployer = DockerDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()