from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
from typing import cast


class InputEditor(QTextEdit):
    send_requested = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText('"↑↓"输入历史导航 "⇧↩"换行 "↩"发送')
        self.installEventFilter(self)

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
                    return True  # 事件已处理
                else:
                    self.send_requested.emit()
        # 其他事件交给默认处理
        return super().eventFilter(obj, event)
