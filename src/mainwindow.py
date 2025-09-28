import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    QEvent,
)
from PySide6.QtGui import QMouseEvent, QAction
from src.forms.mainwindow_ui import Ui_MainWindow
from preferences import Preferences
import time
from typing import cast
from database import DatabaseManager
from chatrobot import ChatRobot
from markdown_it import MarkdownIt
from markdown_it.presets import gfm_like


def setup_markdown():
    config = gfm_like.make()
    md = MarkdownIt(config=config)
    return md


class MainWindow(QMainWindow, Ui_MainWindow):
    message_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.mail_content = sys.stdin.read()
        self.db_manager = DatabaseManager(self)
        self.config = self.db_manager.get_settings()
        # markdown 渲染器
        self.md = setup_markdown()

        self.setupUi(self)

        self.app_instance = self.get_app_instance()

        self.setup_menu()

        self.last_message = ""
        self.statusBar().installEventFilter(self)
        self.chat_history = []
        self.init_history()

        self.client = ChatRobot(mail_content=self.mail_content, parent=self)
        if not self.client:
            return
        self.chat_id = None
        self.js_code = None
        self.init_webengine()
        self.client.init_client()

        self.connect_slots()

    def connect_slots(self):
        """
        连接信号槽
        """
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.input_edit.send_requested.connect(self.on_send_button_clicked)
        self.client.message_updated_signal.connect(self.update_webengine_view)
        self.db_manager.gen_title_request.connect(self.client.gen_title)
        self.client.title_ready_signal.connect(self.db_manager.update_title)
        self.historyListView.index_signal.connect(self.on_history_item_clicked)
        self.client.title_ready_signal.connect(self.update_history)
        self.newchat_btn.clicked.connect(self.new_chat)
        self.historyListView.delete_index_signal.connect(self.remove_history_item)

    def remove_history_item(self, index):
        """删除历史记录项"""
        if 0 <= index < len(self.chat_history):
            chat_to_delete = self.chat_history.pop(index)
            chat_id = chat_to_delete['id']
            self.db_manager.delete_chat(chat_id)

    def on_history_item_clicked(self, index: int):
        """处理历史记录项点击事件"""
        if index >= 0 and index < len(self.chat_history):
            chat = self.chat_history[index]
            self.chat_id = chat['id']
            messages = self.db_manager.get_chat(self.chat_id)['content']
            self.client.messages = messages
            self.update_webengine_view()
            QApplication.processEvents()

    def init_webengine(self):
        with open('src/template.html', 'r') as f:
            html_template = f.read()
            html_template = html_template.replace("{content}", self.convert_markdown_to_html(self.client.messages[0]))
            self.webEngineView.setHtml(html_template)

        with open('src/deepseek.js', 'r') as f:
            self.js_code = f.read()

    def convert_markdown_to_html(self, message: dict) -> str:
        """
        将Markdown内容转换为HTML格式
        """
        return f""" <div class={message["role"]}>
        {self.md.render(message["content"].replace("\\[", "\\\\[").replace("\\]", "\\\\]").replace("\\(", "\\\\(").replace("\\)", "\\\\)"))}
        </div>
""".replace("\\", "\\\\")

    def update_webengine_view(self):
        """
        更新WebEngineView的内容
        """

        # 将所有消息转为HTML内容
        html_content = ""
        for msg in self.client.messages:
            content = self.convert_markdown_to_html(msg)
            html_content += content + "\n\n"

        # 更新HTML内容的部分
        js_code = fr"""
        document.body.innerHTML = `{html_content}`;
        
        {self.js_code}
        """

        # 执行 JavaScript 代码来更新指定部分
        self.webEngineView.page().runJavaScript(js_code)
        self.webEngineView.page().runJavaScript("""
        window.scrollTo(0, document.body.scrollHeight);
        """)

        if self.chat_id is None:
            self.chat_id = self.db_manager.add_chat(self.client.messages)
        else:
            self.db_manager.update_chat(self.chat_id, self.client.messages)

    @staticmethod
    def get_app_instance() -> QApplication:
        """
        获取应用实例
        """
        app_instance = QApplication.instance()
        if app_instance is None:
            app_instance = QApplication(sys.argv)
        return app_instance

    def show_message_on_status_bar(self, message):
        """
        在状态栏显示消息
        """
        self.last_message = message
        self.statusBar().showMessage(message, 5000)

    def on_send_button_clicked(self):
        """
        发送按钮点击时的槽函数
        """
        self.send_button.setEnabled(False)
        content = self.input_edit.toPlainText() + "\n"
        self.client.messages.append({"role": "user", "content": content})
        self.update_webengine_view()
        self.input_edit.clear()
        self.client.send_messages()
        self.send_button.setEnabled(True)

    def closeEvent(self, event):
        """
        关闭事件处理
        """
        if self.client.messages and self.client.messages[-1]["role"] == "assistant":
            last_message = self.client.messages[-1]["content"]
            print(last_message[last_message.find("\n") + 1:])
        time.sleep(0.5)
        super().closeEvent(event)

    def eventFilter(self, obj, event):
        """
        过滤事件，用于处理状态栏点击事件
        :param obj: 事件源对象
        :param event: 事件对象
        :return:bool - 如果事件已处理返回True，否则返回父类处理结果
        """
        if obj == self.statusBar() and event.type() == QEvent.Type.MouseButtonPress:
            mouse_button_press_event = cast(QMouseEvent, event)
            if mouse_button_press_event.button() == Qt.MouseButton.LeftButton and self.last_message:
                self.statusBar().showMessage(self.last_message, 5000)
                return True
        return super().eventFilter(obj, event)

    def setup_menu(self):
        menu_bar = self.menuBar()
        app_menu = menu_bar.addMenu("Application")
        pref_action = QAction("Preferences...", self)
        pref_action.triggered.connect(self.preference)
        pref_action.setMenuRole(QAction.MenuRole.PreferencesRole)
        app_menu.addAction(pref_action)

    def init_history(self):
        """
        初始化聊天记录
        """
        self.chat_history = self.db_manager.get_all_chats()
        self.historyListView.add_items([record['title'] for record in self.chat_history])

    def update_history(self):
        self.historyListView.clear()
        self.init_history()

    def preference(self):
        """
        打开偏好设置窗口
        """
        self.preferences = Preferences()
        self.preferences.show()

    def new_chat(self):
        """
        新建聊天
        """
        self.chat_id = None
        self.client.messages = self.client.messages[:1]
        self.update_webengine_view()
