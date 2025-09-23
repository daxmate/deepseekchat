#! ./.venv/bin/python3
from pyexpat.errors import messages

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow
from PySide6.QtCore import QLibraryInfo, QTranslator


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/icon_mail_chat.svg"))
    app.setApplicationName("DeepSeekChat")
    translation_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator()
    ok = translator.load('qtbase_zh_CN', translation_path)
    if ok:
        app.installTranslator(translator)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
