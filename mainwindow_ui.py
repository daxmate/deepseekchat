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
from PySide6.QtWidgets import (QApplication, QDockWidget, QHBoxLayout, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSplitter,
    QStatusBar, QVBoxLayout, QWidget)

from historylistview import HistoryListView
from inputeditor import InputEditor
from outputtextedit import OutputTextEdit

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.output_edit = OutputTextEdit(self.splitter)
        self.output_edit.setObjectName(u"output_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.output_edit.sizePolicy().hasHeightForWidth())
        self.output_edit.setSizePolicy(sizePolicy)
        self.output_edit.setStyleSheet(u"#output_edit{\n"
" background: #eeeeee;\n"
"}")
        self.output_edit.setReadOnly(True)
        self.splitter.addWidget(self.output_edit)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.input_edit = InputEditor(self.widget)
        self.input_edit.setObjectName(u"input_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.input_edit.sizePolicy().hasHeightForWidth())
        self.input_edit.setSizePolicy(sizePolicy1)
        self.input_edit.setMinimumSize(QSize(0, 100))
        self.input_edit.setMaximumSize(QSize(16777215, 160))
        self.input_edit.setReadOnly(False)

        self.horizontalLayout.addWidget(self.input_edit)

        self.send_button = QPushButton(self.widget)
        self.send_button.setObjectName(u"send_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.send_button.sizePolicy().hasHeightForWidth())
        self.send_button.setSizePolicy(sizePolicy2)
        self.send_button.setMinimumSize(QSize(0, 100))
        self.send_button.setMaximumSize(QSize(16777215, 160))

        self.horizontalLayout.addWidget(self.send_button)

        self.splitter.addWidget(self.widget)

        self.horizontalLayout_2.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget_2 = QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listView = HistoryListView(self.dockWidgetContents_2)
        self.listView.setObjectName(u"listView")

        self.verticalLayout_2.addWidget(self.listView)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget_2)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DeepSeek\u90ae\u4ef6\u52a9\u624b", None))
        self.send_button.setText(QCoreApplication.translate("MainWindow", u"\u53d1\u9001", None))
    # retranslateUi

