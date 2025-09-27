from openai import OpenAI
from PySide6.QtCore import (
    QObject,
    Signal,
    QThread,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow,
)

from outputtextedit import OutputTextEdit


class WorkerThread(QThread):
    """工作线程类，用于在后台执行API调用"""
    result_ready = Signal()
    error_occurred = Signal(str)

    def __init__(self, client, model, messages):
        super().__init__()
        self.client = client
        self.model = model
        self.messages = messages
        self.response = None

    def run(self):
        try:
            self.response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True
            )
            self.result_ready.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatRobot(QObject):
    message_updated_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, mail_content: str, parent: 'MainWindow' = None):
        super().__init__(parent)
        self.parent = parent
        self.messages = []
        self.response = None
        self.role = "email_assistant"
        self.model = self.parent.db_manager.get_setting('model', 'deepseek-chat')
        self.client = OpenAI(api_key=self.parent.db_manager.get_setting('api_key', ''),
                             base_url=self.parent.db_manager.get_setting('api_base_url', ''))
        if self.role == "email_assistant":
            self.mail_content = mail_content
        self.init_config()
        self.worker_thread = None

    def init_config(self):
        self.messages = [
            {
                "role": "system",
                "content": self.parent.db_manager.get_setting("system_prompt"),
            }
        ]
        self.message_updated_signal.emit()

    def trim_messages(self):
        """
        修剪日志消息
        """
        msg = []
        for message in self.messages:
            if message["role"] not in ["reasoning"]:
                msg.append(message)
        return msg

    def send_messages(self):
        """发送消息"""
        # 创建并启动工作线程
        self.worker_thread = WorkerThread(self.client, self.model, self.messages)
        self.worker_thread.result_ready.connect(self.on_worker_result_ready)
        self.worker_thread.error_occurred.connect(self.on_worker_error)
        self.worker_thread.start()

    def on_worker_result_ready(self):
        """工作线程完成时的回调"""
        self.response = self.worker_thread.response
        self.read_stream()

    def on_worker_error(self, error_message):
        """工作线程出错时的回调"""
        self.error_signal.emit(error_message)

    def read_stream(self):
        """读取流式响应"""
        self.messages.append({"role": "assistant", "content": ""})
        last_message = self.messages[-1]

        for chunk in self.response:
            delta = chunk.choices[0].delta.content
            if delta:
                last_message['content'] += delta
                self.message_updated_signal.emit()
                QApplication.processEvents()