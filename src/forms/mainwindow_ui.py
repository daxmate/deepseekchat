# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

from inputeditor import InputEditor
from listview import ListView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.left_column = QWidget(self.centralwidget)
        self.left_column.setObjectName(u"left_column")
        self.verticalLayout = QVBoxLayout(self.left_column)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.historyListView = ListView(self.left_column)
        self.historyListView.setObjectName(u"historyListView")
        self.historyListView.setFrameShape(QFrame.Shape.NoFrame)
        self.historyListView.setFrameShadow(QFrame.Shadow.Sunken)
        self.historyListView.setLineWidth(0)

        self.verticalLayout.addWidget(self.historyListView)

        self.newchat_btn = QPushButton(self.left_column)
        self.newchat_btn.setObjectName(u"newchat_btn")

        self.verticalLayout.addWidget(self.newchat_btn)


        self.horizontalLayout_2.addWidget(self.left_column)

        self.main_area = QWidget(self.centralwidget)
        self.main_area.setObjectName(u"main_area")
        self.verticalLayout_3 = QVBoxLayout(self.main_area)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.webEngineView = QWebEngineView(self.main_area)
        self.webEngineView.setObjectName(u"webEngineView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webEngineView.sizePolicy().hasHeightForWidth())
        self.webEngineView.setSizePolicy(sizePolicy)
        self.webEngineView.setUrl(QUrl(u"about:blank"))

        self.verticalLayout_3.addWidget(self.webEngineView)

        self.line = QFrame(self.main_area)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line)

        self.line_2 = QFrame(self.main_area)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_2)

        self.input_edit = InputEditor(self.main_area)
        self.input_edit.setObjectName(u"input_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.input_edit.sizePolicy().hasHeightForWidth())
        self.input_edit.setSizePolicy(sizePolicy1)
        self.input_edit.setMinimumSize(QSize(0, 0))
        self.input_edit.setMaximumSize(QSize(16777215, 150))
        self.input_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.input_edit.setLineWidth(0)
        self.input_edit.setReadOnly(False)

        self.verticalLayout_3.addWidget(self.input_edit)

        self.verticalLayout_3.setStretch(0, 10)
        self.verticalLayout_3.setStretch(3, 1)

        self.horizontalLayout_2.addWidget(self.main_area)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setMouseTracking(True)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DeepSeek\u90ae\u4ef6\u52a9\u624b", None))
        self.newchat_btn.setText(QCoreApplication.translate("MainWindow", u"New Chat", None))
        self.input_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\"\u2191\u2193\" to navigate input history \"\u21e7\u21a9\" to insert newline \"\u21a9\" to send", None))
    # retranslateUi

