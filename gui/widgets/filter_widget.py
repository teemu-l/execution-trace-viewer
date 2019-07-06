from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QComboBox, QSizePolicy
)


class FilterWidget(QWidget):

    filterBtnClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):

        layout = QHBoxLayout(self)

        self.filter_combo_box = QComboBox()
        self.filter_combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.filter_combo_box.setEditable(True)
        self.filter_combo_box.setMaxVisibleItems(25)
        self.filter_combo_box.setMaximumSize(440, 24)
        self.filter_combo_box.setMinimumSize(220, 24)
        self.filter_combo_box.keyPressEvent = self.on_filter_combo_box_key_pressed
        layout.addWidget(self.filter_combo_box)

        self.filter_btn = QPushButton("Filter", self)
        self.filter_btn.clicked.connect(self.on_filter_btn_clicked)
        self.filter_btn.setMinimumSize(40, 24)
        self.filter_btn.setMaximumSize(40, 24)
        layout.addWidget(self.filter_btn)

        self.setMaximumSize(500, 40)

    def set_sample_filters(self, filters):
        for f in filters:
            self.filter_combo_box.addItem(f)

    def add_sample_filter(self, sample_filter):
        self.filter_combo_box.addItem(sample_filter)

    def on_filter_btn_clicked(self):
        self.filterBtnClicked.emit(self.filter_combo_box.currentText())

    def on_filter_combo_box_key_pressed(self, event):
        """Checks if enter is pressed on filterEdit"""
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.on_filter_btn_clicked()
        QComboBox.keyPressEvent(self.filter_combo_box, event)
