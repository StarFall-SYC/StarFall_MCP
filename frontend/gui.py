"""GUI界面实现"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QLineEdit,
    QTabWidget,
    QComboBox,
    QSpinBox,
    QMessageBox,
)

class ChatMessage:
    """聊天消息"""
    def __init__(self, content: str, is_user: bool = True):
        self.content = content
        self.is_user = is_user

class LLMThread(QThread):
    """LLM处理线程"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, message: str, llm_config: Dict):
        super().__init__()
        self.message = message
        self.llm_config = llm_config
        
        # 初始化事件循环
        import asyncio
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def run(self):
        try:
            from core.llm import LLMConfig, LLMProvider, LLMManager, ChatMessage
            
            # 创建LLM配置
            config = LLMConfig(
                provider=LLMProvider(self.llm_config["llm_type"].lower()),
                api_key=self.llm_config["api_key"],
                api_base=self.llm_config["api_base"],
                model=self.llm_config["model"],
                temperature=self.llm_config["temperature"],
                max_tokens=self.llm_config["max_tokens"]
            )
            
            # 创建LLM实例
            llm = LLMManager.create_llm(config)
            
            # 构建消息
            messages = [ChatMessage(
                role="user",
                content=self.message
            )]
            
            # 异步调用LLM
            response = self.loop.run_until_complete(
                llm.chat(messages)
            )
            
            self.response_ready.emit(response.message.content)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.loop.close()

class SettingsTab(QWidget):
    """设置面板"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        # LLM设置
        llm_group = QVBoxLayout()
        llm_group.addWidget(QLabel("LLM配置"))
        
        # API类型
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API类型:"))
        self.llm_type = QComboBox()
        self.llm_type.addItems(["OpenAI", "Azure", "自定义"])
        self.llm_type.currentTextChanged.connect(self.on_llm_type_changed)
        api_layout.addWidget(self.llm_type)
        llm_group.addLayout(api_layout)

        # API密钥
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API密钥:"))
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        key_layout.addWidget(self.api_key)
        llm_group.addLayout(key_layout)

        # API基础URL
        base_url_layout = QHBoxLayout()
        base_url_layout.addWidget(QLabel("API基础URL:"))
        self.api_base = QLineEdit()
        self.api_base.setPlaceholderText("可选，用于自定义API地址")
        base_url_layout.addWidget(self.api_base)
        llm_group.addLayout(base_url_layout)

        # 模型设置
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))
        self.model = QLineEdit()
        self.model.setPlaceholderText("例如: gpt-3.5-turbo")
        model_layout.addWidget(self.model)
        llm_group.addLayout(model_layout)

        # 温度设置
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("温度:"))
        self.temperature = QSpinBox()
        self.temperature.setRange(0, 20)
        self.temperature.setValue(7)
        self.temperature.setSingleStep(1)
        temp_layout.addWidget(self.temperature)
        llm_group.addLayout(temp_layout)

        # 最大Token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("最大Token:"))
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 10000)
        self.max_tokens.setValue(2000)
        self.max_tokens.setSingleStep(100)
        token_layout.addWidget(self.max_tokens)
        llm_group.addLayout(token_layout)

        # 保存按钮
        save_layout = QHBoxLayout()
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_settings)
        save_layout.addWidget(save_button)
        llm_group.addLayout(save_layout)

        layout.addLayout(llm_group)
        layout.addStretch()
        self.setLayout(layout)

    def on_llm_type_changed(self, llm_type: str):
        """LLM类型改变时的处理"""
        if llm_type == "Azure":
            self.api_base.setPlaceholderText("必填，Azure API端点")
        else:
            self.api_base.setPlaceholderText("可选，用于自定义API地址")

    def save_settings(self):
        """保存配置"""
        from pathlib import Path
        import json

        settings = {
            "llm_type": self.llm_type.currentText(),
            "api_key": self.api_key.text(),
            "api_base": self.api_base.text(),
            "model": self.model.text(),
            "temperature": self.temperature.value() / 10,
            "max_tokens": self.max_tokens.value()
        }

        config_dir = Path.home() / ".starfall"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.json"

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")

    def load_settings(self):
        """加载配置"""
        from pathlib import Path
        import json

        config_file = Path.home() / ".starfall" / "config.json"
        if not config_file.exists():
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                settings = json.load(f)

            self.llm_type.setCurrentText(settings.get("llm_type", "OpenAI"))
            self.api_key.setText(settings.get("api_key", ""))
            self.api_base.setText(settings.get("api_base", ""))
            self.model.setText(settings.get("model", "gpt-3.5-turbo"))
            self.temperature.setValue(int(settings.get("temperature", 0.7) * 10))
            self.max_tokens.setValue(settings.get("max_tokens", 2000))
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置失败: {str(e)}")


class ChatWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.messages: List[ChatMessage] = []
        self.llm_thread: Optional[LLMThread] = None
        self.settings_tab = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('StarFall MCP Chat')
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 标签页
        tabs = QTabWidget()
        
        # 聊天页面
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        # 聊天记录
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)

        # 输入区域
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(60)
        input_layout.addWidget(self.message_input)

        send_button = QPushButton('发送')
        send_button.clicked.connect(self.send_message)
        send_button.setFixedWidth(100)
        input_layout.addWidget(send_button)

        chat_layout.addLayout(input_layout)
        tabs.addTab(chat_widget, '聊天')

        # 设置页面
        self.settings_tab = SettingsTab()
        tabs.addTab(self.settings_tab, '设置')

        layout.addWidget(tabs)

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        # 添加用户消息
        self.add_message(message, True)
        self.message_input.clear()

        # 获取LLM配置
        config = {
            "llm_type": self.settings_tab.llm_type.currentText(),
            "api_key": self.settings_tab.api_key.text(),
            "api_base": self.settings_tab.api_base.text(),
            "model": self.settings_tab.model.text(),
            "temperature": self.settings_tab.temperature.value() / 10,
            "max_tokens": self.settings_tab.max_tokens.value()
        }
        
        # 验证必要配置
        if not config["api_key"]:
            QMessageBox.warning(self, "警告", "请先配置API密钥")
            return
        
        if config["llm_type"].lower() == "azure" and not config["api_base"]:
            QMessageBox.warning(self, "警告", "Azure API需要配置API基础URL")
            return
            
        # 启动LLM处理线程
        self.llm_thread = LLMThread(message, config)
        self.llm_thread.response_ready.connect(self.handle_llm_response)
        self.llm_thread.error_occurred.connect(self.handle_llm_error)
        self.llm_thread.start()

    def add_message(self, content: str, is_user: bool):
        self.messages.append(ChatMessage(content, is_user))
        self.update_chat_history()

    def update_chat_history(self):
        self.chat_history.clear()
        for msg in self.messages:
            prefix = "用户: " if msg.is_user else "AI: "
            self.chat_history.append(f"{prefix}{msg.content}\n")

    def handle_llm_response(self, response: str):
        self.add_message(response, False)

    def handle_llm_error(self, error: str):
        QMessageBox.critical(self, "错误", f"LLM处理出错: {error}")

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()