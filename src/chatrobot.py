from openai import OpenAI
from PySide6.QtCore import (
    QObject,
    Signal,
    QThread,
)
from PySide6.QtWidgets import (
    QApplication
)


class WorkerThread(QThread):
    """工作线程类，用于在后台执行API调用"""
    result_ready = Signal()
    error_occurred = Signal(str)

    def __init__(self, client, model, messages, stream=True):
        super().__init__()
        self.client = client
        self.model = model
        self.messages = messages
        self.response = None
        self.stream = stream

    def run(self):
        try:
            self.response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=self.stream,
            )
            self.result_ready.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class StreamWorkerThread(QThread):
    """流式响应处理线程"""
    chunk_ready = Signal(str)
    stream_complete = Signal()
    error_occurred = Signal(str)

    def __init__(self, response):
        super().__init__()
        self.response = response

    def run(self):
        try:
            for chunk in self.response:
                if self.isInterruptionRequested():
                    break
                delta = chunk.choices[0].delta.content
                if delta:
                    self.chunk_ready.emit(delta)
            self.stream_complete.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatRobot(QObject):
    message_updated_signal = Signal()
    error_signal = Signal(str)
    title_ready_signal = Signal(str)

    def __init__(self, mail_content: str, parent: 'MainWindow' = None):
        super().__init__(parent)
        self.parent = parent
        self.messages = []
        self.response = None
        self.stream = True
        self.role = "email_assistant"
        self.model = self.parent.db_manager.get_setting('model', 'deepseek-chat')
        if self.role == "email_assistant":
            self.mail_content = mail_content
        self.messages = [
            {
                "role": "system",
                "content": self.parent.db_manager.get_setting("system_prompt"),
            }
        ]
        self.message_updated_signal.emit()
        self.worker_thread = None
        self.stream_worker_thread = None

    def init_client(self):
        try:
            self.client = OpenAI(api_key=self.parent.db_manager.get_setting('api_key', ''),
                                 base_url=self.parent.db_manager.get_setting('api_base_url', ''))
        except Exception as e:
            self.error_signal.emit(str(e))

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
        self.worker_thread = WorkerThread(self.client, self.model, self.messages, stream=self.stream)
        self.worker_thread.result_ready.connect(self.on_worker_result_ready)
        self.worker_thread.error_occurred.connect(self.on_worker_error)
        self.worker_thread.start()

    def on_worker_result_ready(self):
        """工作线程完成时的回调"""
        self.response = self.worker_thread.response
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.worker_thread = None
        # 启动流处理线程
        self.start_stream_worker()

    def on_worker_error(self, error_message):
        """工作线程出错时的回调"""
        self.error_signal.emit(error_message)

    def start_stream_worker(self):
        """启动流式响应处理线程"""
        # 添加空的助手消息
        self.messages.append({"role": "assistant", "content": ""})
        # 创建并启动流处理线程
        self.stream_worker_thread = StreamWorkerThread(self.response)
        self.stream_worker_thread.chunk_ready.connect(self.on_chunk_ready)
        self.stream_worker_thread.stream_complete.connect(self.on_stream_complete)
        self.stream_worker_thread.error_occurred.connect(self.on_worker_error)
        self.stream_worker_thread.start()

    def on_chunk_ready(self, delta):
        """收到新的响应片段时的处理"""
        last_message = self.messages[-1]
        last_message['content'] += delta
        self.message_updated_signal.emit()

    def on_stream_complete(self):
        """流式响应完成时的处理"""
        self.stream_worker_thread.quit()
        self.stream_worker_thread.wait()
        self.stream_worker_thread = None

    def gen_title(self):
        """
        生成标题
        """
        message = [
            {
                "role": "user",
                "content": f"""
                Please generate a title for the following content:
                {self.messages[1]["content"]}
""",
            }
        ]
        self.title_worker_thread = WorkerThread(self.client, self.model, message, stream=False)
        self.title_worker_thread.result_ready.connect(self.on_title_worker_result_ready)
        self.title_worker_thread.error_occurred.connect(self.on_worker_error)
        self.title_worker_thread.start()

    def on_title_worker_result_ready(self):
        """标题工作线程完成时的回调"""
        response = self.title_worker_thread.response
        title = response.choices[0].message.content
        self.title_worker_thread.quit()
        self.title_worker_thread.wait()
        self.title_worker_thread = None
        self.title_ready_signal.emit(title)