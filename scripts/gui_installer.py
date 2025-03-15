#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
StarFall MCP GUI安装程序
提供图形化界面的项目下载、环境检查、依赖安装等功能
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PyQt6.QtWidgets import ( QTextEdit,
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QProgressBar, QLabel, QMessageBox,
    QStackedWidget, QWizard, QWizardPage, QComboBox,
    QRadioButton, QButtonGroup, QGroupBox, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import requests
import git
import psutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gui-installer')

class DownloadThread(QThread):
    """项目下载线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url: str, install_path: Path):
        super().__init__()
        self.url = url
        self.install_path = install_path
    
    def run(self):
        try:
            if self.install_path.exists():
                shutil.rmtree(str(self.install_path))
            
            git.Repo.clone_from(
                self.url,
                str(self.install_path),
                progress=lambda op_code, cur_count, max_count, message: \
                    self.progress.emit(int(cur_count / max_count * 100))
            )
            self.finished.emit(True, "项目下载完成")
        except Exception as e:
            self.finished.emit(False, f"下载失败: {str(e)}")

class InstallThread(QThread):
    """依赖安装线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    log_signal = pyqtSignal(str)
    
    def __init__(self, install_path: Path, mode: str = "direct"):
        super().__init__()
        self.install_path = install_path
        self.mode = mode
        self.logger = logging.getLogger('installer')
    
    def log(self, message: str, level: str = "info"):
        """记录日志并发送信号"""
        getattr(self.logger, level)(message)
        self.log_signal.emit(message)
    
    def run(self):
        try:
            # 创建日志目录
            log_dir = self.install_path / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            # 安装依赖
            self.progress.emit(0, "正在准备安装环境...")
            self.log("开始安装依赖包")
            
            if self.mode == "direct":
                # 创建虚拟环境
                self.progress.emit(10, "创建虚拟环境...")
                venv_dir = self.install_path / 'venv'
                subprocess.run(
                    [sys.executable, "-m", "venv", str(venv_dir)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.log("虚拟环境创建成功")
                
                # 获取虚拟环境的Python路径
                python_path = str(venv_dir / 'Scripts' / 'python.exe') if platform.system() == 'Windows' \
                    else str(venv_dir / 'bin' / 'python')
                
                # 升级pip
                self.progress.emit(20, "升级pip...")
                subprocess.run(
                    [python_path, "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.install_path)
                )
                
                # 安装项目依赖
                self.progress.emit(30, "安装项目依赖...")
                result = subprocess.run(
                    [python_path, "-m", "pip", "install", "-e", ".[dev]"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.install_path)
                )
                
                if result.returncode != 0:
                    raise Exception(f"依赖安装失败:\n{result.stderr}")
                
                self.log("项目依赖安装完成")
                self.progress.emit(60, "依赖安装完成")
            
            else:  # Docker模式
                self.progress.emit(30, "准备Docker环境...")
                # TODO: 实现Docker模式的安装逻辑
                self.progress.emit(60, "Docker环境准备完成")
            
            # 生成配置文件
            self.progress.emit(75, "生成配置文件...")
            env_example = self.install_path / '.env.example'
            env_file = self.install_path / '.env'
            if env_example.exists() and not env_file.exists():
                shutil.copy2(str(env_example), str(env_file))
                self.log("配置文件生成成功")
            
            # 创建数据目录
            data_dir = self.install_path / 'data'
            data_dir.mkdir(exist_ok=True)
            
            self.progress.emit(100, "安装完成")
            self.finished.emit(True, "安装成功完成！")
            self.log("安装过程全部完成", "info")
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"安装过程出错: {error_msg}", "error")
            self.finished.emit(False, f"安装失败: {error_msg}")
            raise

class WelcomePage(QWizardPage):
    """欢迎页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("欢迎使用 StarFall MCP 安装向导")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 欢迎信息
        welcome_label = QLabel(
            "<h3>本向导将帮助您完成 StarFall MCP 的安装</h3>\n"
            "<p>安装过程包括：</p>\n"
            "<ul>"
            "<li>从GitHub下载项目</li>"
            "<li>检查系统环境</li>"
            "<li>安装必要依赖</li>"
            "<li>生成配置文件</li>"
            "<li>验证安装</li>"
            "<li>部署服务</li>"
            "</ul>"
        )
        welcome_label.setTextFormat(Qt.TextFormat.RichText)
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        
        # 部署模式选择
        mode_group = QGroupBox("部署模式")
        mode_layout = QVBoxLayout()
        
        self.mode_group = QButtonGroup(self)
        self.direct_mode = QRadioButton("直接部署 - 在本机Python环境中安装")
        self.docker_mode = QRadioButton("Docker部署 - 使用容器化环境（推荐）")
        self.direct_mode.setChecked(True)
        
        self.mode_group.addButton(self.direct_mode)
        self.mode_group.addButton(self.docker_mode)
        
        mode_layout.addWidget(self.direct_mode)
        mode_layout.addWidget(self.docker_mode)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 安装路径配置
        path_group = QGroupBox("安装路径")
        path_layout = QHBoxLayout()
        
        path_label = QLabel("安装目录：")
        self.path_input = QLineEdit(str(Path(os.path.expanduser("~")) / "StarFall_MCP"))
        self.path_input.setPlaceholderText("选择安装目录")
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_path)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # 高级配置
        config_group = QGroupBox("高级配置")
        config_layout = QVBoxLayout()
        
        # 端口配置
        port_layout = QHBoxLayout()
        port_label = QLabel("服务端口：")
        self.port_input = QLineEdit("8000")
        self.port_input.setPlaceholderText("输入端口号（1024-65535）")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        config_layout.addLayout(port_layout)
        
        # 主机配置
        host_layout = QHBoxLayout()
        host_label = QLabel("监听地址：")
        self.host_input = QLineEdit("127.0.0.1")
        self.host_input.setPlaceholderText("输入监听地址（如：127.0.0.1）")
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        config_layout.addLayout(host_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 添加配置验证
        self.port_input.textChanged.connect(self.validate_port)
        self.host_input.textChanged.connect(self.validate_host)
        self.path_input.textChanged.connect(self.validate_path)
        
        self.setLayout(layout)
    
    def browse_path(self):
        """打开文件夹选择对话框"""
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "选择安装目录", self.path_input.text())
        if path:
            self.path_input.setText(path)
    
    def validate_path(self, path: str):
        """验证安装路径输入"""
        install_path = Path(path)
        try:
            if not install_path.is_absolute():
                self.path_input.setStyleSheet("border: 1px solid red;")
                return False
            if install_path.exists() and not install_path.is_dir():
                self.path_input.setStyleSheet("border: 1px solid red;")
                return False
            self.path_input.setStyleSheet("")
            return True
        except Exception:
            self.path_input.setStyleSheet("border: 1px solid red;")
            return False
    
    def validate_port(self, text: str):
        """验证端口号输入"""
        try:
            port = int(text)
            if 1024 <= port <= 65535:
                self.port_input.setStyleSheet("")
                return True
            else:
                self.port_input.setStyleSheet("border: 1px solid red;")
                return False
        except ValueError:
            self.port_input.setStyleSheet("border: 1px solid red;")
            return False
    
    def validate_host(self, text: str):
        """验证主机地址输入"""
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$|^localhost$'
        if re.match(ip_pattern, text):
            self.host_input.setStyleSheet("")
            return True
        else:
            self.host_input.setStyleSheet("border: 1px solid red;")
            return False

class SystemCheckPage(QWizardPage):
    """系统检查页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("系统环境检查")
        
        self.layout = QVBoxLayout()
        self.status_label = QLabel("正在检查系统环境...")
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)
        
        self.is_complete = False
    
    def check_python_version(self) -> Tuple[bool, str]:
        """检查Python版本"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            return False, f"Python版本需要 >= 3.10，当前版本: {platform.python_version()}"
        return True, "Python版本检查通过"
    
    def check_memory(self) -> Tuple[bool, str]:
        """检查内存大小"""
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024 ** 3)
        if memory_gb < 4:
            return False, f"内存大小需要 >= 4GB，当前大小: {memory_gb:.1f}GB"
        return True, "内存大小检查通过"
    
    def check_disk_space(self) -> Tuple[bool, str]:
        """检查磁盘空间"""
        install_path = Path(os.path.expanduser("~")) / "StarFall_MCP"
        parent_path = install_path.parent
        disk = psutil.disk_usage(str(parent_path))
        free_gb = disk.free / (1024 ** 3)
        if free_gb < 1:
            return False, f"可用磁盘空间需要 >= 1GB，当前可用: {free_gb:.1f}GB"
        return True, "磁盘空间检查通过"
    
    def check_docker(self) -> Tuple[bool, str]:
        """检查Docker环境"""
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            return True, "Docker环境检查通过"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "请确保Docker和Docker Compose已正确安装"
    
    def initializePage(self):
        # 获取部署模式
        welcome_page = self.wizard().page(0)
        is_docker_mode = welcome_page.docker_mode.isChecked()
        
        # 执行检查
        checks = [
            (self.check_python_version, "检查Python版本..."),
            (self.check_memory, "检查内存大小..."),
            (self.check_disk_space, "检查磁盘空间...")
        ]
        
        if is_docker_mode:
            checks.append((self.check_docker, "检查Docker环境..."))
        
        # 更新状态
        for check_func, message in checks:
            self.status_label.setText(message)
            QApplication.processEvents()
            ok, result = check_func()
            if not ok:
                QMessageBox.critical(self, "错误", result)
                return
            self.status_label.setText(result)
            QApplication.processEvents()
        
        self.is_complete = True
        self.completeChanged.emit()
    
    def isComplete(self) -> bool:
        return self.is_complete

class DownloadPage(QWizardPage):
    """下载页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("下载项目")
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加状态标签
        self.status_label = QLabel("准备下载...")
        self.status_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CCCCCC;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.layout.addWidget(self.progress_bar)
        
        self.setLayout(self.layout)
        
        self.download_thread = None
        self.is_complete = False
    
    def initializePage(self):
        self.download_thread = DownloadThread(
            "https://github.com/StarFall-SYC/StarFall_MCP.git",
            Path(self.wizard().page(0).path_input.text())
        )
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"下载进度: {value}%")
    
    def download_finished(self, success: bool, message: str):
        if success:
            self.status_label.setText(message)
            self.is_complete = True
            self.completeChanged.emit()
        else:
            QMessageBox.critical(self, "错误", message)
    
    def isComplete(self) -> bool:
        return self.is_complete

class InstallPage(QWizardPage):
    """安装页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("安装依赖")
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加状态标签
        self.status_label = QLabel("准备安装...")
        self.status_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CCCCCC;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.layout.addWidget(self.progress_bar)
        
        # 添加详情文本框
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumHeight(150)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #F5F5F5;
                padding: 5px;
            }
        """)
        self.layout.addWidget(self.detail_text)
        
        self.setLayout(self.layout)
        
        self.install_thread = None
        self.is_complete = False
    
    def initializePage(self):
        self.install_thread = InstallThread(
            Path(self.wizard().page(0).path_input.text())
        )
        self.install_thread.progress.connect(self.update_progress)
        self.install_thread.finished.connect(self.install_finished)
        self.install_thread.start()
    
    def update_progress(self, value: int, message: str):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.detail_text.append(f"[{value}%] {message}")
        self.detail_text.verticalScrollBar().setValue(
            self.detail_text.verticalScrollBar().maximum()
        )
    
    def install_finished(self, success: bool, message: str):
        if success:
            self.status_label.setText(message)
            self.is_complete = True
            self.completeChanged.emit()
        else:
            QMessageBox.critical(self, "错误", message)
    
    def isComplete(self) -> bool:
        return self.is_complete

class VerificationPage(QWizardPage):
    """安装验证页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("安装验证")
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加状态标签
        self.status_label = QLabel("正在验证安装...")
        self.status_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CCCCCC;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.layout.addWidget(self.progress_bar)
        
        # 添加详情文本框
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumHeight(150)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #F5F5F5;
                padding: 5px;
            }
        """)
        self.layout.addWidget(self.detail_text)
        
        self.setLayout(self.layout)
        
        self.is_complete = False
    
    def initializePage(self):
        try:
            install_path = Path(self.wizard().page(0).path_input.text())
            # 运行测试
            self.status_label.setText("运行测试...")
            self.progress_bar.setValue(50)
            self.detail_text.append("[50%] 开始运行测试...")
            QApplication.processEvents()
            
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests"],
                check=True,
                capture_output=True,
                text=True,
                cwd=str(install_path)
            )
            
            self.detail_text.append(result.stdout)
            self.detail_text.verticalScrollBar().setValue(
                self.detail_text.verticalScrollBar().maximum()
            )
            
            self.status_label.setText("验证完成")
            self.progress_bar.setValue(100)
            self.detail_text.append("[100%] 验证完成")
            self.is_complete = True
            self.completeChanged.emit()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "错误", f"安装验证失败: {e.stderr}")
    
    def isComplete(self) -> bool:
        return self.is_complete

class DeploymentPage(QWizardPage):
    """部署页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("部署服务")
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加状态标签
        self.status_label = QLabel("正在部署服务...")
        self.status_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CCCCCC;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.layout.addWidget(self.progress_bar)
        
        # 添加详情文本框
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumHeight(150)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #F5F5F5;
                padding: 5px;
            }
        """)
        self.layout.addWidget(self.detail_text)
        
        self.setLayout(self.layout)
        
        self.is_complete = False
    
    def initializePage(self):
        try:
            install_path = Path(self.wizard().page(0).path_input.text())
            welcome_page = self.wizard().page(0)
            is_docker_mode = welcome_page.docker_mode.isChecked()
            
            self.detail_text.append("[0%] 开始部署服务...")
            self.progress_bar.setValue(0)
            QApplication.processEvents()
            
            if is_docker_mode:
                # Docker部署
                self.status_label.setText("构建Docker镜像...")
                self.progress_bar.setValue(30)
                QApplication.processEvents()
                
                subprocess.run(['docker-compose', 'build'], check=True, cwd=str(install_path))
                
                self.status_label.setText("启动Docker服务...")
                self.progress_bar.setValue(60)
                QApplication.processEvents()
                
                subprocess.run(['docker-compose', 'up', '-d'], check=True, cwd=str(install_path))
                
                self.status_label.setText("检查服务状态...")
                self.progress_bar.setValue(90)
                QApplication.processEvents()
                
                subprocess.run(['docker-compose', 'ps'], check=True, cwd=str(install_path))
            else:
                # 直接部署
                self.status_label.setText("启动服务...")
                self.progress_bar.setValue(50)
                QApplication.processEvents()
                
                cmd = [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000']
                subprocess.Popen(cmd, cwd=str(install_path))
            
            self.status_label.setText("部署完成")
            self.progress_bar.setValue(100)
            self.is_complete = True
            self.completeChanged.emit()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "错误", f"部署失败: {str(e)}")
    
    def isComplete(self) -> bool:
        return self.is_complete

class CompletionPage(QWizardPage):
    """完成页面"""
    def __init__(self):
        super().__init__()
        self.setTitle("安装完成")
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加完成图标
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon.fromTheme("dialog-ok").pixmap(64, 64))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.icon_label)
        
        # 添加完成信息标签
        self.completion_label = QLabel()
        self.completion_label.setTextFormat(Qt.TextFormat.RichText)
        self.completion_label.setOpenExternalLinks(True)
        self.completion_label.setWordWrap(True)
        self.layout.addWidget(self.completion_label)
        
        self.setLayout(self.layout)
    
    def initializePage(self):
        install_path = self.wizard().page(0).path_input.text()
        self.completion_label.setText(
            "<h2>StarFall MCP 已成功安装到您的系统！</h2>"
            "<p>安装信息：</p>"
            "<ul>"
            f"<li>安装目录：{install_path}</li>"
            "<li>服务已启动，请访问 <a href='http://localhost:8000'>http://localhost:8000</a> 查看服务是否正常运行</li>"
            "<li>配置文件位置：.env</li>"
            "<li>日志文件位置：logs/starfall.log</li>"
            "</ul>"
            "<p>下一步：</p>"
            "<ul>"
            "<li>查看<a href='https://github.com/StarFall/starfall-mcp/docs'>项目文档</a>了解如何使用</li>"
            "<li>加入<a href='https://github.com/StarFall/starfall-mcp/discussions'>社区讨论</a>获取帮助</li>"
            "<li>报告问题请访问<a href='https://github.com/StarFall/starfall-mcp/issues'>Issues</a></li>"
            "</ul>"
            "<p style='text-align: center; margin-top: 20px;'><b>感谢您的使用！</b></p>"
        )

class InstallerWizard(QWizard):
    """安装向导主窗口"""
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("StarFall MCP 安装向导")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.DisabledBackButtonOnLastPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.button(QWizard.WizardButton.BackButton).setEnabled(False)
        
        # 设置页面
        self.addPage(WelcomePage())
        self.addPage(SystemCheckPage())
        self.addPage(DownloadPage())
        class InstallWizard(QWizard):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("StarFall MCP 安装向导")
                
                # 设置窗口图标
                icon_path = str(Path(__file__).parent / 'app.ico')
                self.setWindowIcon(QIcon(icon_path))
                
                # 添加任务栏图标
                if QApplication.instance():
                    QApplication.instance().setWindowIcon(QIcon(icon_path))
                
                # 设置窗口图标（新增部分）
                self.setWindowIcon(QIcon(icon_path))
                
                # 添加任务栏图标（新增部分）
                if hasattr(Qt, 'ApplicationAttribute'):
                    QApplication.instance().setWindowIcon(QIcon(icon_path))
                    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar, True)

                self.addPage(WelcomePage())
                self.addPage(SystemCheckPage())
                self.addPage(DownloadPage())
                self.addPage(InstallPage())
                self.addPage(VerificationPage())
                self.addPage(DeploymentPage())
        self.addPage(CompletionPage())
        
        # 设置窗口大小
        self.resize(600, 400)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    icon_path = str(Path(__file__).parent / 'app.ico')
    app.setWindowIcon(QIcon(icon_path))
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    wizard = InstallerWizard()
    
    # 设置窗口居中显示
    wizard.show()
    desktop = app.primaryScreen().geometry()
    wizard.move((desktop.width() - wizard.width()) // 2,
                (desktop.height() - wizard.height()) // 2)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()