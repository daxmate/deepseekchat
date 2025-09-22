import sys
import os
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
)
from PySide6.QtCore import (
    Qt,
    QEvent,
)
from PySide6.QtGui import (
    QKeyEvent,
)
from mainwindow_ui import Ui_MainWindow
from openai import OpenAI
from typing import cast
import copy
import time
import requests
from historylistview import HistoryListView
from resources import dsc
from inputeditor import InputEditor
from platform import Platform


class MainWindow(QMainWindow, Ui_MainWindow, Platform):
    def __init__(self):
        super().__init__()
        Platform.__init__(self)
        self.mail_content = sys.stdin.read()
        self.api_key = self.deepseek_api_key
        self.output_edit = None
        self.messages = []
        self.setupUi(self)

        self.provider = "deepseek"
        self.client = None
        if self.provider == "deepseek":
            from deepseek import DeepSeek
            self.client = DeepSeek(api_key=self.deepseek_api_key)

        if not self.client:
            return
        self.app_instance = self.get_app_instance()

        # 设置主题与系统主题一致
        self.setup_theme()

        self.response = None
        self.final_response = None
        self.init_config()

        self.connect_slots()

    def init_config(self):
        if self.config:
            self.messages = [
                {
                    "role": "system",
                    "content": self.config['prompts']['email_reply']['system'],
                },
                {
                    "role": "user",
                    "content": self.config['prompts']['email_reply']['user'].format(
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

    def connect_slots(self):
        """
        连接信号槽
        """
        self.input_edit.textChanged.connect(self.on_input_edit_text_changed)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.update_output_edit()
        self.app_instance.styleHints().colorSchemeChanged.connect(self.setup_theme)
        self.input_edit.send_requested.connect(self.on_send_button_clicked)

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

    def update_output_edit(self):
        """
        更新输出编辑框的内容
        """
        self.output_edit.clear()
        text = ""
        for message in self.messages:
            for key, val in message.items():
                text += key + ":\t" + val + "\n"
        self.output_edit.setText(text)
        self.output_edit.verticalScrollBar().setValue(self.output_edit.verticalScrollBar().maximum())

    def on_input_edit_text_changed(self):
        """
        输入编辑框文本改变时的槽函数
        """
        msg = copy.deepcopy(self.messages)
        user_command = "请按邮件原文回复并包含以下信息：\n" + self.input_edit.toPlainText()
        if msg[-1]["role"] == "user":
            msg[-1]["content"] = self.messages[-1]["content"] + user_command
        else:
            msg.append({"role": "user", "content": user_command})

        self.update_output_edit()

    def log(self, message):
        """
        记录日志消息
        """
        self.messages.append({"role": "log", "content": message + "\n"})
        self.update_output_edit()
        self.output_edit.verticalScrollBar().setValue(self.output_edit.verticalScrollBar().maximum())

    def trim_messages(self):
        """
        修剪日志消息
        """
        msg = []
        for message in self.messages:
            if message["role"] not in ["log", "reasoning"]:
                msg.append(message)
        return msg

    def on_send_button_clicked(self):
        """
        发送按钮点击时的槽函数
        """
        self.send_button.setEnabled(False)
        self.messages[1]["content"] += self.input_edit.toPlainText()
        msg = self.trim_messages()
        self.update_output_edit()
        self.input_edit.clear()
        self.start_stream()

    def start_stream(self):
        """
        开始获取流式响应
        """
        try:
            # 清空之前的输出
            self.log("正在获取响应...")

            msg = self.trim_messages()

            # 调用API获取流式响应
            self.response = self.client.chat.completions.create(
                model="deepseek-reasoner",
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
            self.reasoning_text = ""
            self.messages.append({"role": "reasoning", "content": self.reasoning_text})
            self.messages.append({"role": "assistant", "content": self.final_response})
            for chunk in self.response:
                # 检查是否有内容
                if chunk.choices and chunk.choices[0].delta:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        self.final_response += content
                        # 更新UI显示
                        self.messages[-1]["content"] = self.final_response
                    else:
                        if chunk.choices[0].delta.reasoning_content:
                            reasoning_content = chunk.choices[0].delta.reasoning_content
                            self.reasoning_text += reasoning_content
                            self.messages[-2]["content"] = self.reasoning_text
                    self.update_output_edit()

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
        return self.client.models.list()

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
