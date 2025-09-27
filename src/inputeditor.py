from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
from typing import cast

from urllib3 import Retry


class InputEditor(QTextEdit):
    send_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        self.histories = []
        self.history_index = -1  # -1 表示空白位置，>=0 表示历史记录索引

    def eventFilter(self, obj, event: QEvent):
        """
        事件过滤器，处理输入框的按键事件
        Shift+Enter换行
        """
        # 检查事件是否是输入框的按键按下事件
        if obj is self and event.type() == QEvent.Type.KeyPress:
            key_event = cast(QKeyEvent, event)
            key = key_event.key()
            # 判断是否按下了回车键
            if key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
                # 判断是否同时按下了Shift键
                if key_event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Shift+Enter：插入换行符
                    cursor = self.textCursor()
                    cursor.insertText("\n")
                    return True
                else:
                    self.histories.append(self.toPlainText())
                    self.history_index = -1  # 发送消息后重置到空白位置
                    self.send_requested.emit()
                    return True
        if obj is self and event.type() == QEvent.Type.KeyRelease:
            key_event = cast(QKeyEvent, event)
            key = key_event.key()
            if key == Qt.Key.Key_Up:
                if self.histories:
                    # 如果当前在空白位置(-1)，则跳转到最后一个历史记录
                    if self.history_index == -1:
                        self.history_index = len(self.histories) - 1
                    else:
                        # 向上导航到前一个历史记录
                        self.history_index = self.history_index - 1
                    self.update_text()
            elif key == Qt.Key.Key_Down:
                if self.histories:
                    # 如果当前在最后一个历史记录，则跳转到空白位置
                    if self.history_index == len(self.histories) - 1:
                        self.history_index = -1
                    elif self.history_index == -1:
                        # 如果当前在空白位置，则跳转到第一个历史记录
                        self.history_index = 0
                    else:
                        # 向下导航到后一个历史记录
                        self.history_index = self.history_index + 1
                    self.update_text()
        # 其他事件交给默认处理
        return super().eventFilter(obj, event)

    def update_text(self):
        # 如果索引为-1，表示空白位置
        if self.history_index == -1:
            self.clear()
        elif self.histories and self.history_index < len(self.histories):
            self.setText(self.histories[self.history_index])
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)