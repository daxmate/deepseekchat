#! ./.venv/bin/python3
from pyexpat.errors import messages

import requests
import sys

from PySide6.QtGui import QIcon
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

        self.input_edit.textChanged.connect(self.on_input_edit_text_changed)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.input_edit.installEventFilter(self)
        self.update_output_edit(self.messages)

    # 添加事件过滤器处理回车发送和Shift+Enter换行
    def eventFilter(self, obj, event: QEvent):
        # 检查事件是否是输入框的按键按下事件
        if obj is self.input_edit and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            # 判断是否按下了回车键
            if key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
                # 判断是否同时按下了Shift键
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
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

    def update_output_edit(self, messages):
        self.output_edit.clear()
        text = ""
        for message in messages:
            for key, val in message.items():
                text += key + ":\t" + val + "\n"
        self.output_edit.setText(text)
        self.output_edit.verticalScrollBar().setValue(self.output_edit.verticalScrollBar().maximum())

    def on_input_edit_text_changed(self):
        messages = copy.deepcopy(self.messages)
        if messages[-1]["role"] == "user":
            messages[-1]["content"] += self.input_edit.toPlainText()
        else:
            messages.append({"role": "user", "content": self.input_edit.toPlainText()})

        if self.input_edit.toPlainText():
            messages[-1]["content"] = "请在回复中包含以下内容：\n" + self.input_edit.toPlainText()

        self.update_output_edit(messages)

    def log(self, message):
        self.messages.append({"role": "log", "content": message + "\n"})
        self.update_output_edit(self.messages)
        self.output_edit.verticalScrollBar().setValue(self.output_edit.verticalScrollBar().maximum())

    def trim_log_message(self):
        messages = []
        for message in self.messages:
            if message["role"] != "log":
                messages.append(message)
        return messages

    def on_send_button_clicked(self):
        self.send_button.setEnabled(False)
        self.messages[1]["content"] += self.input_edit.toPlainText()
        messages = self.trim_log_message()
        self.update_output_edit(messages)
        self.input_edit.clear()
        self.start_stream()

    # api key存放在~/dotfiles/ai_api_keys中，内容为 export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxx
    def get_deepseek_api_key(self):
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
        try:
            # 清空之前的输出
            self.log("正在获取响应...")

            messages = self.trim_log_message()

            # 调用API获取流式响应
            self.response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )
            self.read_stream()
        except Exception as e:
            self.log(str(e))

    def read_stream(self):
        # 实现流式响应处理
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
        if self.final_response:
            print(self.final_response[8:])
        time.sleep(0.5)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/icon_mail_chat.svg"))
    app.setApplicationName("DeepSeekChat")
    win = DeepSeekChat()
    win.show()
    sys.exit(app.exec())
