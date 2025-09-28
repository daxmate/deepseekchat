from typing import Any

from PySide6.QtWidgets import QListView, QMainWindow
from PySide6.QtCore import Qt, QModelIndex, QAbstractListModel, Signal
from PySide6.QtGui import QKeyEvent


class ItemModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.items = []

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.items)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        item = self.items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item
        return None


class ListView(QListView):
    index_signal = Signal(int)
    delete_index_signal = Signal(int)

    def __init__(self, parent=None, model: ItemModel = None):
        super().__init__(parent)
        self.model = model or ItemModel()
        self.setModel(self.model)
        # 连接clicked信号到处理函数
        self.clicked.connect(self.on_item_clicked)

    def add_items(self, items):
        self.model.items.extend(items)
        self.model.layoutChanged.emit()

    def on_item_clicked(self, index: QModelIndex):
        """处理项目点击事件"""
        if index.isValid():
            self.index_signal.emit(index.row())

    def clear(self):
        self.model.items.clear()
        self.model.layoutChanged.emit()

    def remove_item(self, index: int):
        """删除指定索引的项目"""
        if 0 <= index < len(self.model.items):
            self.model.beginRemoveRows(QModelIndex(), index, index)
            self.model.items.pop(index)
            self.model.endRemoveRows()
            self.model.layoutChanged.emit()
            self.delete_index_signal.emit(index)
            return True
        return False

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，按下Delete键删除选中的条目"""
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            # 获取所有选中的索引
            selected_indexes = self.selectedIndexes()
            if selected_indexes:
                # 创建一个包含有效索引的行号列表
                rows_to_remove = []
                for index in selected_indexes:
                    if index.isValid():
                        rows_to_remove.append(index.row())

                # 从后往前删除，避免索引偏移问题
                for row in sorted(rows_to_remove, reverse=True):
                    self.remove_item(row)
        else:
            # 其他按键事件交给父类处理
            super().keyPressEvent(event)
