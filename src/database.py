import sqlite3
import json
from datetime import datetime
from PySide6.QtCore import QObject
from platform import *


class DatabaseManager(QObject):
    def __init__(self):
        super().__init__()
        self.db_path = os.path.join(get_config_dir(), 'deepseekchat.db')

        # 初始化数据库
        self.init_database()
        # 初始化默认设置
        self.init_default_settings()

    def init_database(self):
        """初始化数据库，创建必要的表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建历史对话记录表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS chat_history
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           date
                           TEXT
                           NOT
                           NULL,
                           title
                           TEXT
                           NOT
                           NULL,
                           content
                           TEXT
                           NOT
                           NULL
                       )
                       ''')

        # 修改表结构
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS settings
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           key
                           TEXT
                           NOT
                           NULL,
                           value
                           TEXT
                           NOT
                           NULL
                       )
                       ''')

        conn.commit()
        conn.close()

    def add_chat(self, title, messages):
        """添加一条新的聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 将消息列表转换为JSON字符串
        content = json.dumps(messages)

        # 获取当前时间
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 插入记录
        cursor.execute(
            "INSERT INTO chat_history (date, title, content) VALUES (?, ?, ?)",
            (date, title, content)
        )

        chat_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return chat_id

    def get_chat(self, chat_id):
        """获取特定ID的聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chat_history WHERE id = ?", (chat_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                'id': row[0],
                'date': row[1],
                'title': row[2],
                'content': json.loads(row[3])
            }
        return None

    def get_all_chats(self):
        """获取所有聊天记录的基本信息（不包括完整内容）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, date, title FROM chat_history ORDER BY date DESC")
        rows = cursor.fetchall()

        conn.close()

        return [{'id': row[0], 'date': row[1], 'title': row[2]} for row in rows]

    def update_chat(self, chat_id, title=None, messages=None):
        """更新聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if title:
            cursor.execute("UPDATE chat_history SET title = ? WHERE id = ?", (title, chat_id))

        if messages:
            content = json.dumps(messages)
            cursor.execute("UPDATE chat_history SET content = ? WHERE id = ?", (content, chat_id))

        conn.commit()
        conn.close()

    def delete_chat(self, chat_id):
        """删除聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM chat_history WHERE id = ?", (chat_id,))

        conn.commit()
        conn.close()

    def save_setting(self, key, value):
        """保存设置，支持同一键名多个值"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if isinstance(value, list):
            for item in value:
                cursor.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (key, item)
                )
        else:
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )

        conn.commit()
        conn.close()

    def get_settings(self, key):
        """获取指定键的所有值"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        rows = cursor.fetchall()

        conn.close()

        return [row[0] for row in rows]  # 返回值列表

    def delete_setting(self, key, value=None):
        """删除设置，可以删除指定键的所有值或特定值"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if value:
            cursor.execute("DELETE FROM settings WHERE key = ? AND value = ?", (key, value))
        else:
            cursor.execute("DELETE FROM settings WHERE key = ?", (key,))

        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        """获取设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()

        conn.close()

        return row[0] if row else default

    def is_settings_empty(self):
        """检查设置表是否为空"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]

        conn.close()

        return count == 0

    def init_default_settings(self):
        """初始化默认设置"""
        # 检查设置表是否为空
        if self.is_settings_empty():
            # 默认设置字典
            default_settings = {
                # 提供者相关设置
                "provider": "deepseek",
                # 模型相关设置
                "model": "deepseek-chat",
                # api_key
                "api_key": "",
                # api_base_url
                "api_base_url": "https://api.deepseek.com",
                # default system prompt
                "system_prompt": self.tr("You are a helpful assistant that provides accurate and concise answers."),
                # 界面相关设置
                "theme": "system",  # system, light, dark
                "font_size": "12",
                # API相关设置
                "api_timeout": "30",
                "max_tokens": "1000",
                # 历史记录相关设置
                "save_history": "true",
                "max_history_count": "50"
            }

            # 将默认设置写入数据库
            for key, values in default_settings.items():
                for value in values:
                    self.save_setting(key, value)

            print(self.tr("Default settings have been initialized"))


if __name__ == '__main__':
    db = DatabaseManager()
    db.init_default_settings()
