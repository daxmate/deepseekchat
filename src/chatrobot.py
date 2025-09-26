from openai import OpenAI
from PySide6.QtCore import (
    QObject,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow,
)

from outputtextedit import OutputTextEdit


class ChatRobot(QObject):
    message_signal = Signal(str)

    def __init__(self, mail_content: str, parent: 'MainWindow'=None):
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

    def init_config(self):
        self.messages = [
            {
                "role": "system",
                "content": self.parent.db_manager.get_setting("system_prompt"),
            }
        ]

    def trim_messages(self):
        """
        修剪日志消息
        """
        msg = []
        for message in self.messages:
            if message["role"] not in ["reasoning"]:
                msg.append(message)
        return msg

    def send_messages(self, output_edit: OutputTextEdit):
        """
        开始获取流式响应
        """
        try:
            # 清空之前的输出
            self.message_signal.emit(self.tr("Sending messages..."))

            # 根据模型类型决定是否修剪消息
            if self.model == "deepseek-reasoner":
                msg = self.trim_messages()
            else:
                msg = self.messages

            # 调用API获取流式响应
            self.response = self.client.chat.completions.create(
                model=self.model,
                messages=msg,
                stream=True
            )
            self.read_stream(output_edit)
        except Exception as e:
            self.message_signal.emit(str(e))

    def read_stream(self, output_edit: OutputTextEdit):
        """读取流式响应"""
        try:
            if self.parent.config["role"] == "email_assistant":
                final_response = self.parent.config["mail_content_prompt"]
            else:
                final_response = ""

            # 根据模型类型决定处理方式
            if self.model == "deepseek-reasoner":
                # 处理推理模型的逻辑
                reasoning_text = ""
                self.messages.append({"role": "reasoning", "content": reasoning_text})
                self.messages.append({"role": "assistant", "content": final_response})

                # 获取当前reasoning消息的索引（应该是倒数第二个）
                reasoning_index = len(self.messages) - 2

                # 在处理流式响应时，确保reasoning部分是展开的
                if output_edit and hasattr(output_edit, 'message_folded_states'):
                    output_edit.message_folded_states[reasoning_index] = False  # False表示展开

                # 添加标志来跟踪reasoning是否已经结束
                reasoning_ended = False

                for chunk in self.response:
                    # 检查是否有内容
                    if chunk.choices and chunk.choices[0].delta:
                        # 检查当前chunk是否包含reasoning内容
                        has_reasoning_content = hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[
                            0].delta.reasoning_content

                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            final_response += content
                            # 更新UI显示
                            self.messages[-1]["content"] = final_response

                            # 如果之前有reasoning内容但现在没有了，说明reasoning已经结束
                            if not reasoning_ended and reasoning_text:
                                reasoning_ended = True
                                # reasoning结束后立即折叠
                                if output_edit and hasattr(output_edit, 'message_folded_states'):
                                    output_edit.message_folded_states[reasoning_index] = True  # True表示折叠
                        else:
                            if has_reasoning_content:
                                reasoning_content = chunk.choices[0].delta.reasoning_content
                                reasoning_text += reasoning_content
                                self.messages[-2]["content"] = reasoning_text
                            else:
                                # 如果之前有reasoning内容但现在没有了，说明reasoning已经结束
                                if not reasoning_ended and reasoning_text:
                                    reasoning_ended = True
                                    # reasoning结束后立即折叠
                                    if output_edit and hasattr(output_edit, 'message_folded_states'):
                                        output_edit.message_folded_states[reasoning_index] = True  # True表示折叠

                        output_edit.update_display()

                        # 确保UI及时更新
                        QApplication.processEvents()

                # 确保在所有内容处理完毕后，如果reasoning还没折叠，就折叠它
                if output_edit and hasattr(output_edit, 'message_folded_states'):
                    output_edit.message_folded_states[reasoning_index] = True  # True表示折叠
                    output_edit.update_display()  # 应用折叠状态
            else:
                # 处理普通聊天模型的逻辑
                self.messages.append({"role": "assistant", "content": final_response})

                for chunk in self.response:
                    # 检查是否有内容
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        final_response += content
                        # 更新UI显示
                        self.messages[-1]["content"] = final_response
                        output_edit.update_display()

                        # 确保UI及时更新
                        QApplication.processEvents()

        except Exception as e:
            self.message_signal.emit(self.tr("Error processing streaming response: " + str(e)))
