import os
import sys


def get_config_dir():
    if sys.platform == 'darwin':
        config_dir = os.path.expanduser('~/Library/Application Support/DeepSeekChat')
    elif sys.platform == 'win32':
        config_dir = os.path.join(os.getenv('APPDATA'), 'DeepSeekChat')
    else:
        config_dir = os.path.expanduser('~/.config/DeepSeekChat')
    # 确保配置目录存在
    os.makedirs(config_dir, exist_ok=True)
    return config_dir
