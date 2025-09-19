import os
import json
import sys


class Platform:
    def __init__(self):
        if sys.platform == 'darwin':
            config_dir = os.path.expanduser('~/Library/Application Support/DeepSeekChat')
        else:
            config_dir = os.path.expanduser('~/.config/DeepSeekChat')
        self._config_path = os.path.join(config_dir, 'config.json')

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

    # 加载配置文件
    def load_config(self):
        if os.path.exists(self._config_path):
            return json.load(open(self._config_path, 'r'))
        return {}

    @property
    def config_path(self):
        return self._config_path
