from forms.preferences_ui import Ui_Preferences
from PySide6.QtWidgets import QWidget

class Preferences(QWidget, Ui_Preferences):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
