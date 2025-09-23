import sys

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QMenu,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    QEvent,
)
from PySide6.QtGui import QMouseEvent, QAction
from mainwindow_ui import Ui_MainWindow
from preferences import Preferences
import copy
import time
from resources import dsc
from platform import Platform
from typing import cast


class MainWindow(QMainWindow, Ui_MainWindow):
    message_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.platform = Platform()
        self.mail_content = sys.stdin.read()
        self.api_key = self.platform.deepseek_api_key
        self.setupUi(self)

        self.provider = "deepseek"
        self.client = None
        if self.provider == "deepseek":
            from deepseek import DeepSeek
            self.client = DeepSeek(api_key=self.platform.deepseek_api_key, parent=self)

        if not self.client:
            return
        self.app_instance = self.get_app_instance()

        # 设置主题与系统主题一致
        self.setup_theme()
        self.setup_menu()

        self.statusBar().setMouseTracking(True)
        self.statusBar().installEventFilter(self)

        self.connect_slots()

    def connect_slots(self):
        """
        连接信号槽
        """
        self.input_edit.textChanged.connect(self.on_input_edit_text_changed)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.update_output_edit()
        self.app_instance.styleHints().colorSchemeChanged.connect(self.setup_theme)
        self.input_edit.send_requested.connect(self.on_send_button_clicked)
        self.platform.error.connect(self.show_message_on_status_bar)
        self.message_signal.connect(self.show_message_on_status_bar)
        if self.client and hasattr(self.client, 'message_signal'):
            self.client.message_signal.connect(lambda msg: self.show_message_on_status_bar(msg),
                                               Qt.ConnectionType.QueuedConnection)

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
        self.output_edit.update_display(self.client.messages)

    def on_input_edit_text_changed(self):
        """
        输入编辑框文本改变时的槽函数
        """
        msg = copy.deepcopy(self.client.messages)
        user_command = self.tr(
            "Please reply according to the original email and include the following information: \n") + self.input_edit.toPlainText()
        if msg[-1]["role"] == "user":
            msg[-1]["content"] = self.client.messages[-1]["content"] + user_command
        else:
            msg.append({"role": "user", "content": user_command})

        self.update_output_edit()

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
        self.client.messages[1]["content"] += self.input_edit.toPlainText()
        self.update_output_edit()
        self.input_edit.clear()
        self.client.send_messages(self.output_edit)

    def closeEvent(self, event):
        """
        关闭事件处理
        """
        if self.client.messages:
            print(self.client.messages[-1]["content"][8:])
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
            self.output_edit.setStyleSheet("*{ background: #2d2d2d; color: #ffffff; }")
            # 可以根据需要设置更多控件的样式
        else:
            # 亮色模式
            self.output_edit.setStyleSheet("*{ background: #eeeeee; color: #000000; }")

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
