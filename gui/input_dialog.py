"""Dialog to get values from user"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
)


class InputDialog(QDialog):
    def __init__(self, parent=None, title="Title", data=[], on_ok_clicked=None):
        QWidget.__init__(self, parent)

        self.setWindowFlags(
            Qt.Dialog
            | Qt.WindowTitleHint
            | Qt.CustomizeWindowHint
            | Qt.WindowCloseButtonHint
        )
        self.data = data
        self.output_data = []
        self.on_ok_clicked = on_ok_clicked

        mainLayout = QGridLayout()

        # create labels and input widgets
        for i, item in enumerate(self.data):

            label_widget = QLabel(item["label"] + ":")

            if isinstance(item["data"], bool):
                input_widget = QCheckBox()
                input_widget.setChecked(item["data"])
            elif isinstance(item["data"], (int, str)):
                default = str(item.get("data", ""))
                input_widget = QLineEdit(default)
            elif isinstance(item["data"], list):
                input_widget = QComboBox()
                input_widget.addItems(item["data"])
            else:
                print(f"Error. Unknown data type: {type(item['data'])}")
                return

            if "tooltip" in item:
                input_widget.setToolTip(str(item["tooltip"]))
                label_widget.setToolTip(str(item["tooltip"]))

            item["widget"] = input_widget

            mainLayout.addWidget(label_widget, i, 0)
            mainLayout.addWidget(input_widget, i, 1)

        ok_btn = QPushButton("Ok")
        ok_btn.clicked.connect(self.on_ok_btn_clicked)
        mainLayout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.on_cancel_btn_clicked)
        mainLayout.addWidget(cancel_btn)

        self.setLayout(mainLayout)
        self.setWindowTitle(title)

    def on_ok_btn_clicked(self):
        data = []
        for item in self.data:
            if isinstance(item["data"], bool):
                data.append(item["widget"].isChecked())
            elif isinstance(item["data"], str):
                data.append(item["widget"].text())
            elif isinstance(item["data"], int):
                text = item["widget"].text()
                text = text.strip()  # remove whitespaces
                try:
                    if "0x" in text:
                        data.append(int(text, 16))
                    else:
                        data.append(int(text))
                except ValueError:
                    print(f"Error, could not convert {text} to integer.")
                    return
            elif isinstance(item["data"], list):
                data.append(int(item["widget"].currentIndex()))

        # call callback function to check the data
        if self.on_ok_clicked and not self.on_ok_clicked(data):
            return

        self.output_data = data
        self.close()

    def on_cancel_btn_clicked(self):
        self.output_data = []
        self.close()

    def get_data(self):
        return self.output_data
