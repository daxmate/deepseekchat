#! ./.venv/bin/python3
from pyexpat.errors import messages

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/icon_mail_chat.svg"))
    app.setApplicationName("DeepSeekChat")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
