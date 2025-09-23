from typing import Any

from PySide6.QtWidgets import QListView, QMainWindow
from PySide6.QtCore import Qt, QModelIndex, QAbstractListModel


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
    def __init__(self, parent=None, model: ItemModel = None):
        super().__init__(parent)
        self.model = model or ItemModel()
        self.setModel(self.model)

    def add_items(self, items):
        self.model.items.extend(items)
        self.model.layoutChanged.emit()
