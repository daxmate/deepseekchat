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
import copy
import time
from typing import cast
from database import DatabaseManager
from chatrobot import ChatRobot
from markdown_it import MarkdownIt
from markdown_it.presets import gfm_like


class MainWindow(QMainWindow, Ui_MainWindow):
    message_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.mail_content = sys.stdin.read()
        self.db_manager = DatabaseManager()
        self.config = self.db_manager.get_settings()
        # markdown 渲染器
        self.md = self.setup_markdown()

        self.setupUi(self)

        self.app_instance = self.get_app_instance()

        # 设置主题与系统主题一致
        self.setup_theme()
        self.setup_menu()

        self.last_message = ""
        self.statusBar().installEventFilter(self)

        self.client = ChatRobot(mail_content=self.mail_content, parent=self)
        if not self.client:
            return

        self.connect_slots()
        self.update_webengine_view()

    def setup_markdown(self):
        config = gfm_like.make()
        md = MarkdownIt(config=config)
        return md

    def connect_slots(self):
        """
        连接信号槽
        """
        self.input_edit.textChanged.connect(self.on_input_edit_text_changed)
        # self.send_button.clicked.connect(self.on_send_button_clicked)
        # self.update_output_edit()
        # self.app_instance.styleHints().colorSchemeChanged.connect(self.setup_theme)
        self.input_edit.send_requested.connect(self.on_send_button_clicked)
        # self.message_signal.connect(self.show_message_on_status_bar)
        # if self.client and hasattr(self.client, 'message_signal'):
        #     self.client.message_signal.connect(lambda msg: self.show_message_on_status_bar(msg),
        #                                        Qt.ConnectionType.QueuedConnection)
        self.client.message_updated_signal.connect(self.update_webengine_view)

    def update_webengine_view(self):
        """
        更新输出编辑框的内容
        """

        html_template = open('src/template.html', 'r').read()
        text = ""
        for msg in self.client.messages:
            content = self.md.render(msg["content"])
            text += content

        html = html_template.format(content=text)
        self.webEngineView.setHtml(html)
        self.webEngineView.repaint()
        QApplication.processEvents()

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

    # def update_output_edit(self):
    #     """
    #     更新输出编辑框的内容
    #     """
    #     self.update_webengine_view()

    def on_input_edit_text_changed(self):
        """
        输入编辑框文本改变时的槽函数
        """
        msg = self.client.messages
        if self.config["role"] == "mail_assistant" and len(msg) == 1:
            user_command = self.config["mail_prefix"] + self.input_edit.toPlainText()
        else:
            user_command = self.input_edit.toPlainText()
        if msg[-1]["role"] == "user":
            msg[-1]["content"] = user_command
        else:
            msg.append({"role": "user", "content": user_command})

        self.update_webengine_view()

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
            self.webEngineView.setStyleSheet("*{ background: #2d2d2d; color: #ffffff; }")
            # 可以根据需要设置更多控件的样式
        else:
            # 亮色模式
            self.webEngineView.setStyleSheet("*{ background: #eeeeee; color: #000000; }")

        # 设置全局调色板
        self.app_instance.setPalette(palette)

    def setup_menu(self):
        menu_bar = self.menuBar()
        app_menu = menu_bar.addMenu("Application")
        pref_action = QAction("Preferences...", self)
        pref_action.triggered.connect(self.preference)
        pref_action.setMenuRole(QAction.MenuRole.PreferencesRole)
        app_menu.addAction(pref_action)

    def preference(self):
        """
        打开偏好设置窗口
        """
        self.preferences = Preferences()
        self.preferences.show()
