from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class MemTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(MemTableWidget, self).__init__(parent)
        self.mem_data = []

    def set_data(self, data):
        """Sets table data and updates it"""
        self.mem_data = data
        self.populate()

    def populate(self):
        """Fills table with data"""
        if self.mem_data is None or not self.mem_data:
            self.setRowCount(0)
        else:
            self.setRowCount(len(self.mem_data))
            for i, mem in enumerate(self.mem_data):
                self.setItem(i, 0, QTableWidgetItem(mem["access"]))
                self.setItem(i, 1, QTableWidgetItem(hex(mem["addr"])))
                self.setItem(i, 2, QTableWidgetItem(hex(mem["value"])))
            self.update_column_widths()

    def update_column_widths(self):
        """Updates column widths of a TableWidget to match the content"""
        self.setVisible(False)  # fix ui glitch with column widths
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        self.setVisible(True)
