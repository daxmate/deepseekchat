#! ./.venv/bin/python3
from pyexpat.errors import messages

import requests
import sys
from typing import cast, Optional

from PySide6.QtGui import QIcon, QKeyEvent
from openai import OpenAI
import os
from deepseekchat import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QEvent
import copy
import time
import json
from resources import dsc

# 修复配置文件路径处理逻辑
if sys.platform == 'darwin':
    config_dir = os.path.expanduser('~/Library/Application Support/DeepSeekChat')
else:
    config_dir = os.path.expanduser('~/.config/DeepSeekChat')
CONFIG_PATH = os.path.join(config_dir, 'config.json')

# 确保配置目录存在
os.makedirs(config_dir, exist_ok=True)


# 加载配置文件
def load_config():
    if os.path.exists(CONFIG_PATH):
        return json.load(open(CONFIG_PATH, 'r'))
    return {}


class DeepSeekChat(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.mail_content = sys.stdin.read()
        self.deepseek_api_key = None
        self.output_edit = None
        self.get_deepseek_api_key()
        self.setupUi(self)
        self.client = OpenAI(api_key=self.deepseek_api_key, base_url="https://api.deepseek.com")
        self.app_instance = self.get_app_instance()

        # 添加主题适应代码
        self.setup_theme()
        # 监听系统主题变化

        self.response = None
        self.final_response = None
        config = load_config()
        if config:
            self.messages = [
                {
                    "role": "system",
                    "content": config['prompts']['email_reply']['system'].format(
                        name=config['user_info']['name'],
                        title=config['user_info']['title'],
                        company=config['user_info']['company'],
                    ),
                },
                {
                    "role": "user",
                    "content": config['prompts']['email_reply']['user'].format(
                        mail_content=self.mail_content,
                    ),
                },
            ]
        else:
            self.messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的邮件回复助手",
                }
            ]

        self.connect_slots()

    def connect_slots(self):
        """
        连接信号槽
        """
        self.input_edit.textChanged.connect(self.on_input_edit_text_changed)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.input_edit.installEventFilter(self)
        self.update_output_edit(self.messages)
        self.app_instance.styleHints().colorSchemeChanged.connect(self.setup_theme)

    @staticmethod
    def get_app_instance() -> QApplication:
        """
        获取应用实例
        """
        app_instance = QApplication.instance()
        if app_instance is None:
            app_instance = QApplication(sys.argv)
        return app_instance

    # 添加用于检测系统主题的代码
    def is_system_dark_mode(self):
        """
        检查系统是否为深色模式
        """
        # 对于Qt 6.5+版本，可以使用colorScheme()方法
        if self.app_instance.styleHints() and hasattr(self.app_instance.styleHints(), 'colorScheme'):
            return self.app_instance.styleHints().colorScheme() == Qt.ColorScheme.Dark
        else:
            return False

    def eventFilter(self, obj, event: QEvent):
        """
        事件过滤器，处理输入框的按键事件
        处理回车发送和Shift+Enter换行
        """
        # 检查事件是否是输入框的按键按下事件
        if obj is self.input_edit and event.type() == QEvent.Type.KeyPress:
            key_event = cast(QKeyEvent, event)
            key = key_event.key()
            # 判断是否按下了回车键
            if key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
                # 判断是否同时按下了Shift键
                if key_event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Shift+Enter：插入换行符
                    cursor = self.input_edit.textCursor()
                    cursor.insertText("\n")
                    return True  # 事件已处理
                else:
                    # 单独Enter：触发发送
                    self.on_send_button_clicked()
                    return True  # 事件已处理
        # 其他事件交给默认处理
        return super().eventFilter(obj, event)

    def update_output_edit(self, msg):
        """
        更新输出编辑框的内容
        """
        self.output_edit.clear()
        text = ""
        for message in msg:
            for key, val in message.items():
                text += key + ":\t" + val + "\n"
        self.output_edit.setText(text)
        self.output_edit.verticalScrollBar().setValue(self.output_edit.verticalScrollBar().maximum())

    def on_input_edit_text_changed(self):
        """
        输入编辑框文本改变时的槽函数
        """
        msg = copy.deepcopy(self.messages)
        if msg[-1]["role"] == "user":
            msg[-1]["content"] = self.messages[-1][
                                          "content"] + "请在回复中包含以下内容：\n" + self.input_edit.toPlainText()
        else:
            msg.append({"role": "user", "content": "请在回复中包含以下内容：\n" + self.input_edit.toPlainText()})

        self.update_output_edit(msg)

    def log(self, message):
        """
        记录日志消息
        """
        self.messages.append({"role": "log", "content": message + "\n"})
        self.update_output_edit(self.messages)
        self.output_edit.verticalScrollBar().setValue(self.output_edit.verticalScrollBar().maximum())

    def trim_log_message(self):
        """
        修剪日志消息
        """
        msg = []
        for message in self.messages:
            if message["role"] != "log":
                msg.append(message)
        return msg

    def on_send_button_clicked(self):
        """
        发送按钮点击时的槽函数
        """
        self.send_button.setEnabled(False)
        self.messages[1]["content"] += self.input_edit.toPlainText()
        msg = self.trim_log_message()
        self.update_output_edit(msg)
        self.input_edit.clear()
        self.start_stream()

    # api key存放在~/dotfiles/ai_api_keys中，内容为 export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxx
    def get_deepseek_api_key(self):
        """
        获取Deepseek API密钥
        """
        api_path = os.path.expanduser("~/dotfiles/ai_api_keys")
        if os.path.exists(api_path):
            with open(os.path.expanduser("~/dotfiles/ai_api_keys")) as f:
                for line in f.readlines():
                    _, name_key = line.split()
                    name, key = name_key.split("=")
                    if name.strip() == "DEEPSEEK_API_KEY":
                        self.deepseek_api_key = key.strip()
        else:
            print("请在~/dotfiles/ai_api_keys中添加DEEPSEEK_API_KEY")
            return
        if not self.deepseek_api_key:
            return

    def start_stream(self):
        """
        开始获取流式响应
        """
        try:
            # 清空之前的输出
            self.log("正在获取响应...")

            msg = self.trim_log_message()

            # 调用API获取流式响应
            self.response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=msg,
                stream=True
            )
            self.read_stream()
        except Exception as e:
            self.log(str(e))

    def read_stream(self):
        """
        读取流式响应
        """
        try:
            self.final_response = "回复邮件如下：\n"
            self.messages.append({"role": "assistant", "content": self.final_response})
            for chunk in self.response:
                # 检查是否有内容
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    self.final_response += content
                    # 更新UI显示
                    self.messages[-1]["content"] = self.final_response
                    self.update_output_edit(self.messages)
                    # 确保UI及时更新
                    QApplication.processEvents()
            self.send_button.setEnabled(True)

        except Exception as e:
            self.log(f"流式响应处理错误: {str(e)}")

    def closeEvent(self, event):
        """
        关闭事件处理
        """
        if self.final_response:
            print(self.final_response[8:])
        time.sleep(0.5)
        super().closeEvent(event)

    def list_deepseek_models(self):
        """
        获取Deepseek模型列表
        """
        url = "https://api.deepseek.com/models"

        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Request failed: {resp.status_code}, {resp.text}")
        data = resp.json()
        # 返回结构里有 data 字段，是一个模型列表
        models = data.get("data", [])
        return models

    def setup_theme(self):
        """
        根据系统主题设置应用配色
        """
        is_dark = self.is_system_dark_mode()

        # 获取当前应用的调色板
        palette = self.app_instance.palette()

        # 根据主题模式设置颜色
        if is_dark:
            # 暗色模式
            self.output_edit.setStyleSheet("*{ background: #2d2d2d; color: #ffffff; }")
            # 可以根据需要设置更多控件的样式
        else:
            # 亮色模式
            self.output_edit.setStyleSheet("*{ background: #eeeeee; color: #000000; }")

        # 设置全局调色板
        self.app_instance.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/icon_mail_chat.svg"))
    app.setApplicationName("DeepSeekChat")
    win = DeepSeekChat()
    win.show()
    sys.exit(app.exec())
