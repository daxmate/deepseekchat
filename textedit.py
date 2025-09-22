from PySide6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PySide6.QtCore import Qt, QPoint
from mainwindow import MainWindow


class TextEdit(QTextEdit):
    def __init__(self, reasoning_text, summary="思考中……", parent=None):
        super().__init__()
        self.parent = parent
        self.setReadOnly(True)
        self.reasoning_text = reasoning_text.strip()
        self.summary = summary
        self.folded = True

        self.update_display()
        self.connect_slots()

    def connect_slots(self):
        app_instance = MainWindow.get_app_instance()
        app_instance.styleHints().colorSchemeChanged.connect(self.update_display)

    def mousePressEvent(self, event):
        # 点击任何地方就切换折叠状态（你也可以改成点击第一行才切换）
        position = event.position().toPoint()
        cursor = self.cursorForPosition(position)
        if cursor.blockNumber() == 0:  # 只允许点击第一行切换
            self.folded = not self.folded
            self.update_display()
        else:
            super().mousePressEvent(event)

    def update_display(self):
        """根据折叠状态更新显示"""
        self.clear()
        cursor = self.textCursor()
        palette = QApplication.palette()
        # 获取当前应用程序的调色板
        fmt = QTextCharFormat()
        # 使用次要文本颜色（通常用于提示性或辅助性文本）
        fmt.setForeground(palette.color(palette.ColorRole.PlaceholderText))

        if self.folded:
            # 折叠状态：只显示一行
            cursor.insertText("▶ " + self.summary)
        else:
            # 展开状态：显示标题 + reasoning 内容
            cursor.insertText("▼ " + self.summary + "\n")

            cursor.insertText(self.reasoning_text)
        # 使用当前主题的次要文本颜色来显示 reasoning 内容
        cursor.setCharFormat(fmt)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        reasoning = """Step 1: Identify problem
Step 2: Break into sub-steps
Step 3: Compute final result
Step 4: Verify correctness"""

        viewer = TextEdit(reasoning)
        layout.addWidget(viewer)


if __name__ == "__main__":
    app = QApplication([])
    demo = Demo()
    demo.resize(600, 300)
    demo.show()
    app.exec()
