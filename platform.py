import os
import json
import sys

from PySide6.QtCore import QObject, Signal


class Platform(QObject):
    error = Signal(str)
    def __init__(self):
        super().__init__()
        if sys.platform == 'darwin':
            config_dir = os.path.expanduser('~/Library/Application Support/DeepSeekChat')
        else:
            config_dir = os.path.expanduser('~/.config/DeepSeekChat')
        self._config_path = os.path.join(config_dir, 'config.json')

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

    # 加载配置文件
    @property
    def config(self):
        if os.path.exists(self._config_path):
            return json.load(open(self._config_path, 'r'))
        return {}

    @property
    def config_path(self):
        return self._config_path

    # api key存放在~/dotfiles/ai_api_keys中，内容为 export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxx
    @property
    def deepseek_api_key(self):
        """
        获取Deepseek API密钥
        """
        api_path = os.path.expanduser("~/dotfiles/ai_api_keys")
        if os.path.exists(api_path):
            with open(os.path.expanduser("~/dotfiles/ai_api_keys")) as f:
                for line in f.readlines():
                    _, name_key = line.split()
                    name, key = name_key.split("=")
                    if name.strip() == "DEEPSEEK_API_KEY":
                        return key.strip()
        elif self.config:
            return self.config.get("DEEPSEEK_API_KEY", None)

        if not self.deepseek_api_key:
            self.error.emit("Deepseek API key not found. Please set it in the config file.")
            return None
        return None
