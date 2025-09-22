import sys

from PySide6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout
from PySide6.QtGui import QTextCharFormat, QTextCursor, QFont, QColor


class OutputTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setReadOnly(True)
        self.summary = "思考中……"
        self.messages = None
        # 存储每个message的折叠状态
        self.message_folded_states = {}

        # self.update_display()
        self.connect_slots()

    def connect_slots(self):
        app_instance = QApplication.instance()
        if app_instance is None:
            app_instance = QApplication(sys.argv)
        app_instance.styleHints().colorSchemeChanged.connect(self.update_display)

    def mousePressEvent(self, event):
        # 确定点击位置对应的消息
        position = event.position().toPoint()
        cursor = self.cursorForPosition(position)
        block_number = cursor.blockNumber()

        # 查找点击的是哪个message
        message_index = self.get_message_index_from_block(block_number)

        # 如果找到了对应的message，则切换其折叠状态
        if message_index is not None:
            self.toggle_message_fold(message_index)
            self.update_display()
        else:
            super().mousePressEvent(event)

    def get_message_index_from_block(self, block_number):
        """根据行号获取对应的消息索引"""
        if not self.messages:
            return None

        # 跟踪当前处理的行号
        current_block = 0

        # 检查每个消息占用的行范围
        for i, message in enumerate(self.messages):
            role = message.get("role", "").lower()

            # 标题行（如果是reasoning类型）
            if role == "reasoning":
                # 如果点击的是标题行，直接返回当前消息索引
                if current_block == block_number:
                    return i
                current_block += 1

            # 内容行
            content_lines = message.get("content", "").count('\n') + 1

            # 检查点击的行是否在当前消息范围内
            if current_block <= block_number < current_block + content_lines:
                return i

            current_block += content_lines

        return None

    def toggle_message_fold(self, message_index):
        """切换指定消息的折叠状态"""
        self.message_folded_states[message_index] = not self.message_folded_states.get(message_index, True)

    def update_display(self, messages=None):
        """根据每个消息的折叠状态更新显示"""
        if messages:
            self.messages = messages

        if not self.messages:
            return

        self.clear()
        cursor = self.textCursor()
        palette = QApplication.palette()

        # 创建两种不同的文本格式
        reasoning_format = QTextCharFormat()
        normal_format = QTextCharFormat()

        # 设置reasoning文本样式
        reasoning_text_color = palette.color(palette.ColorRole.PlaceholderText)
        reasoning_format.setForeground(reasoning_text_color)
        reasoning_font = QFont()
        reasoning_font.setItalic(True)  # 设置斜体
        reasoning_font.setPointSize(12)  # 设置字号
        reasoning_format.setFont(reasoning_font)

        # 设置normal文本样式
        normal_text_color = palette.color(palette.ColorRole.Text)
        normal_format.setForeground(normal_text_color)
        normal_font = QFont()
        normal_font.setBold(False)  # 不加粗
        normal_font.setPointSize(12)  # 设置字号
        normal_format.setFont(normal_font)

        # 保存默认格式
        default_format = cursor.charFormat()

        for i, message in enumerate(self.messages):
            role = message.get("role", "").lower()
            content = message.get("content", "")

            # 获取当前消息的折叠状态
            is_folded = self.message_folded_states.get(i, True)

            # 只对reasoning类型的消息应用折叠功能
            if role == "reasoning":
                # 显示折叠/展开图标和标题 - 使用normal格式
                cursor.setCharFormat(reasoning_format)
                if is_folded:
                    cursor.insertText("▶ " + self.summary + "\n")
                else:
                    cursor.insertText("▼ " + self.summary + "\n")

                # 如果展开，显示内容 - 使用reasoning格式
                if not is_folded:
                    # 先保存当前光标位置
                    cursor_pos = cursor.position()
                    # 插入文本
                    cursor.insertText(content + "\n")
                    # 创建新光标以选择刚插入的文本
                    select_cursor = QTextCursor(self.document())
                    select_cursor.setPosition(cursor_pos)
                    select_cursor.setPosition(cursor.position(), QTextCursor.MoveMode.KeepAnchor)
                    # 应用样式到选中的文本
                    select_cursor.setCharFormat(reasoning_format)
                    # 恢复原光标位置
                    cursor.setPosition(cursor.position())
            else:
                # 非reasoning类型的消息始终显示 - 使用normal格式
                # 先保存当前光标位置
                cursor_pos = cursor.position()
                # 插入文本
                cursor.insertText(content + "\n")
                # 创建新光标以选择刚插入的文本
                select_cursor = QTextCursor(self.document())
                select_cursor.setPosition(cursor_pos)
                select_cursor.setPosition(cursor.position(), QTextCursor.MoveMode.KeepAnchor)
                # 应用样式到选中的文本
                select_cursor.setCharFormat(normal_format)
                # 恢复原光标位置
                cursor.setPosition(cursor.position())

        # 恢复默认格式
        cursor.setCharFormat(default_format)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        messages = [
            {"role": "reasoning", "content": """Step 1: Identify problem
Step 2: Break into sub-steps
Step 3: Compute final result
Step 4: Verify correctness"""},
            {"role": "user", "content": "user command"},
            {"role": "reasoning", "content": """Another reasoning block
With multiple lines
For demonstration"""}
        ]

        viewer = OutputTextEdit()
        viewer.update_display(messages)
        layout.addWidget(viewer)


if __name__ == "__main__":
    app = QApplication([])
    demo = Demo()
    demo.resize(600, 300)
    demo.show()
    app.exec()
