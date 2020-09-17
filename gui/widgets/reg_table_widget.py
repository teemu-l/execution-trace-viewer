import string

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor

from core import prefs


class RegTableWidget(QTableWidget):

    regCheckBoxChanged = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super(RegTableWidget, self).__init__(parent)
        self.printer = print
        self.regs = {}
        self.modified_regs = []
        self.modified_regs_ignore = ["eip", "rip"]
        self.filtered_regs = []
        self.checked_regs = {}
        self.menu = None
        if prefs.USE_DARK_THEME:
            self.hl_color = QColor("darkRed")
        else:
            self.hl_color = QColor("#fcabab")

    def create_context_menu(self):
        """Initializes context menu for mouse right click"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.menu = QMenu(self)
        print_action = QAction("Print selected cells", self)
        print_action.triggered.connect(self.print_selected_cells)
        self.menu.addAction(print_action)

    def onCellChanged(self, row, col):
        if col > 0:
            return
        item = self.item(row, 0)
        state = item.checkState()
        state_bool = state == Qt.Checked
        reg_name = item.text()

        self.checked_regs[reg_name] = state
        self.regCheckBoxChanged.emit(reg_name, state_bool)

    def on_custom_context_menu_requested(self):
        """Context menu callback for mouse right click"""
        if self.menu is not None:
            self.menu.popup(QCursor.pos())

    def set_data(self, regs, modified_regs):
        """Sets table data and populates the table"""
        if self.filtered_regs:
            temp_regs = {}
            for reg, value in regs.items():
                if reg in self.filtered_regs:
                    temp_regs[reg] = value
                regs = temp_regs
        self.regs = regs
        self.modified_regs = modified_regs
        self.populate()

    def populate(self):
        """Populates the register table"""
        try:
            self.cellChanged.disconnect()
        except Exception:
            pass

        if self.rowCount() != len(self.regs):
            self.setRowCount(len(self.regs))
        if not self.regs:
            return

        i = 0
        for reg, value in self.regs.items():
            if self.filtered_regs and reg not in self.filtered_regs:
                continue
            regname_item = QTableWidgetItem(reg)
            regname_item.setFlags(
                Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )
            check_state = self.checked_regs.get(reg, Qt.Unchecked)
            regname_item.setCheckState(check_state)
            self.setItem(i, 0, regname_item)

            if isinstance(value, int):
                hex_str = hex(value)
                if 0 < value < 255 and chr(value) in string.printable:
                    hex_str += f"  '{chr(value)}'"

                hex_item = QTableWidgetItem(hex_str)

                hex_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                dec_item = QTableWidgetItem(str(value))
                dec_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.setItem(i, 1, hex_item)
                self.setItem(i, 2, dec_item)
            else:
                self.setItem(i, 1, QTableWidgetItem(value))

            if reg in self.modified_regs and reg not in self.modified_regs_ignore:
                self.item(i, 0).setBackground(self.hl_color)
                self.item(i, 1).setBackground(self.hl_color)
                self.item(i, 2).setBackground(self.hl_color)
            i += 1

        if "eflags" in self.regs:
            eflags = self.regs["eflags"]
            flags = {
                "c": eflags & 1,  # carry
                "p": (eflags >> 2) & 1,  # parity
                # "a": (eflags >> 4) & 1,  # aux_carry
                "z": (eflags >> 6) & 1,  # zero
                "s": (eflags >> 7) & 1,  # sign
                # "d": (eflags >> 10) & 1, # direction
                # "o":  (eflags >> 11) & 1 # overflow
            }
            flags_text = f"C:{flags['c']} P:{flags['p']} Z:{flags['z']} S:{flags['s']}"
            self.setRowCount(i + 1)
            self.setItem(i, 0, QTableWidgetItem("flags"))
            self.setItem(i, 1, QTableWidgetItem(flags_text))

        self.cellChanged.connect(self.onCellChanged)

    def print(self, msg: str):
        if self.printer:
            self.printer(msg)
        else:
            print(msg)

    def print_selected_cells(self):
        """Prints selected cells"""
        items = self.selectedItems()

        if len(items) < 1:
            return

        rows = {}
        for item in items:
            row = item.row()
            if row not in rows:
                rows[row] = [item.text()]
            else:
                rows[row].append(item.text())

        for row in rows.values():
            self.print(" ".join(row))
