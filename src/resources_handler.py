from PySide6.QtCore import QIODevice, QFile


def get_resource(path: str) -> str:
    file = QFile(path)
    if file.open(QIODevice.OpenModeFlag.ReadOnly):
        content = file.readAll().toStdString()
        file.close()
        return content
    return ""
