from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QColor


class RegTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super(RegTableWidget, self).__init__(parent)
        self.regs = {}
        self.modified_regs = []
        self.filtered_regs = []

    def set_data(self, regs, modified_regs):
        """Sets table data and updates it"""
        if self.filtered_regs:
            temp_regs = {}
            for reg, value in regs.items():
                if reg in self.filtered_regs:
                    temp_regs[reg] = value
                regs = temp_regs
        self.regs = regs
        self.modified_regs = modified_regs
        self.update()

    def update(self):
        """Fills table with registers"""
        if self.rowCount() != len(self.regs):
            self.setRowCount(len(self.regs))
        if not self.regs:
            return

        i = 0
        for reg, value in self.regs.items():
            if self.filtered_regs and reg not in self.filtered_regs:
                continue
            self.setItem(i, 0, QTableWidgetItem(reg))
            if isinstance(value, int):
                self.setItem(i, 1, QTableWidgetItem(hex(value)))
                self.setItem(i, 2, QTableWidgetItem(str(value)))
            else:
                self.setItem(i, 1, QTableWidgetItem(value))
            if reg in self.modified_regs:
                self.item(i, 0).setBackground(QColor(100, 100, 150))
                self.item(i, 1).setBackground(QColor(100, 100, 150))
                self.item(i, 2).setBackground(QColor(100, 100, 150))
            i += 1

        if "eflags" in self.regs:
            eflags = self.regs["eflags"]
            flags = {
                "c": eflags & 1,           # carry
                "p": (eflags >> 2) & 1,    # parity
                # "a": (eflags >> 4) & 1,  # aux_carry
                "z": (eflags >> 6) & 1,    # zero
                "s": (eflags >> 7) & 1,    # sign
                # "d": (eflags >> 10) & 1, # direction
                # "o":  (eflags >> 11) & 1 # overflow
            }
            flags_text = f"C:{flags['c']} P:{flags['p']} Z:{flags['z']} S:{flags['s']}"
            self.setRowCount(i + 1)
            self.setItem(i, 0, QTableWidgetItem("flags"))
            self.setItem(i, 1, QTableWidgetItem(flags_text))
