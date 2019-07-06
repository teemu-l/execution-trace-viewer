from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal


class FindWidget(QWidget):

    findBtnClicked = pyqtSignal(str, int, int)

    def __init__(self, parent=None):
        super(FindWidget, self).__init__(parent)
        self.last_direction = 1
        self.init_ui()

    def init_ui(self):

        layout = QHBoxLayout(self)

        self.find_label = QLabel("Find:")
        self.find_label.setMaximumSize(35, 24)
        layout.addWidget(self.find_label)

        self.find_combo_box = QComboBox()
        self.find_combo_box.setMaximumSize(100, 24)
        layout.addWidget(self.find_combo_box)

        self.find_edit = QLineEdit()
        self.find_edit.setMaximumSize(140, 24)
        self.find_edit.returnPressed.connect(
            lambda: self.on_find_btn_clicked(self.last_direction)
        )
        layout.addWidget(self.find_edit)

        self.prev_btn = QPushButton("prev", self)
        self.prev_btn.clicked.connect(lambda: self.on_find_btn_clicked(-1))
        self.prev_btn.setMinimumSize(40, 24)
        self.prev_btn.setMaximumSize(40, 24)
        layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("next", self)
        self.next_btn.clicked.connect(lambda: self.on_find_btn_clicked(1))
        self.next_btn.setMinimumSize(40, 24)
        self.next_btn.setMaximumSize(40, 24)
        layout.addWidget(self.next_btn)

        layout.setAlignment(Qt.AlignLeft)

    def set_fields(self, fields):
        for field in fields:
            self.find_combo_box.addItem(field)

    def add_field(self, field):
        self.find_combo_box.addItem(field)

    def on_find_btn_clicked(self, direction):
        """Find next or prev button clicked"""
        self.last_direction = direction
        field_index = self.find_combo_box.currentIndex()
        keyword = self.find_edit.text()
        self.findBtnClicked.emit(keyword, field_index, direction)
