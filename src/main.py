#! ./.venv/bin/python3
from pyexpat.errors import messages

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow
from PySide6.QtCore import QLibraryInfo, QTranslator

from resources.dsc import qt_resource_data


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/icon_mail_chat.svg"))
    app.setApplicationName("DeepSeekChat")
    translation_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qt_translator = QTranslator()
    ok = qt_translator.load('qtbase_zh_CN', translation_path)
    if ok:
        app.installTranslator(qt_translator)
    app_translator = QTranslator()
    ok = app_translator.load('resources/translations/app_zh_CN.qm')
    if ok:
        app.installTranslator(app_translator)
    webengine_translator = QTranslator()
    ok = webengine_translator.load('qtwebengine_zh_CN', translation_path)
    if ok:
        app.installTranslator(webengine_translator)
    # 加载样式表
    with open("src/style.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
