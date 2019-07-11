from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import pyqtSignal, Qt, QItemSelectionModel
from PyQt5.QtGui import QCursor

from core.bookmark import Bookmark


class TraceTableWidget(QTableWidget):

    rowChanged = pyqtSignal(int)
    bookmarkCreated = pyqtSignal(Bookmark)
    commentEdited = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super(TraceTableWidget, self).__init__(parent)
        self.printer = self.print_debug
        self.trace = []
        self.pagination = None
        self.menu = None
        self.init_ui()

    def init_ui(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.custom_context_menu_requested
        )
        self.itemChanged.connect(self.item_changed)

    def selectionChanged(self, selected, deselected):
        """Method reimplementation for QTableWidget selection change"""
        row_ids = self.get_selected_row_ids()
        if row_ids:
            row_id = row_ids[0]
            self.rowChanged.emit(row_id)
        super(TraceTableWidget, self).selectionChanged(selected, deselected)

    def create_bookmark(self):
        """Create a bookmark from selected rows"""
        selected_rows = self.selectedItems()
        if not selected_rows:
            self.print_debug("Could not create a bookmark. Nothing selected.")
            return

        addr = self.item(selected_rows[0].row(), 1).text()
        disasm = self.item(selected_rows[0].row(), 3).text()
        comment = self.item(selected_rows[0].row(), 4).text()

        selected_row_ids = self.get_selected_row_ids()
        first_row_id = selected_row_ids[0]
        last_row_id = selected_row_ids[-1]
        bookmark = Bookmark(
            startrow=first_row_id,
            endrow=last_row_id,
            addr=addr,
            disasm=disasm,
            comment=comment
        )
        self.bookmarkCreated.emit(bookmark)

    def custom_context_menu_requested(self):
        """Context menu for mouse right click"""
        if self.menu is not None:
            self.menu.popup(QCursor.pos())

    def get_selected_row_ids(self):
        """Returns IDs of all selected rows.

        returns:
            list: Sorted list of row ids
        """
        # use a set so we don't get duplicate ids
        row_ids_set = set(
            self.item(index.row(), 0).text() for index in self.selectedIndexes()
        )
        try:
            row_ids_list = [int(i) for i in row_ids_set]
        except ValueError:
            self.print_debug("Error. Values in the first column must be integers.")
            return None
        return sorted(row_ids_list)

    def go_to_row(self, row):
        if self.pagination is not None:
            page = int(row / self.pagination.rows_per_page) + 1
            row = row % self.pagination.rows_per_page
            if page != self.pagination.current_page:
                self.pagination.set_current_page(page)
        self.scrollToItem(self.item(row, 3), QAbstractItemView.PositionAtCenter)
        self.select_row(row)

    def item_changed(self, item):
        cell_type = item.whatsThis()
        if cell_type == "comment":
            row = self.currentRow()
            if row < 0:
                self.print_debug("Error, could not edit trace.")
                return
            row_id = int(self.item(row, 0).text())
            self.commentEdited.emit(row_id, item.text())
        else:
            self.print_debug("Only comment editing allowed for now...")

    def print_debug(self, msg):
        print(msg)

    def print_selected_cells(self):
        """Prints selected cells"""
        if self.printer is None:
            return
        items = self.selectedItems()
        for item in items:
            self.printer(item.text())

    def select_row(self, row):
        """Selects a row in a table"""
        self.clearSelection()
        item = self.item(row, 0)
        self.setCurrentItem(
            item,
            QItemSelectionModel.Select
            | QItemSelectionModel.Rows
            | QItemSelectionModel.Current,
        )

    def set_data(self, data):
        self.trace = data
        if self.pagination is not None:
            self.update_pagination()
        # self.update()

    def update(self):
        try:
            self.itemChanged.disconnect()
        except Exception:
            pass

        trace = self.trace
        if trace is None or not trace:
            self.setRowCount(0)
            return

        if self.pagination is not None:
            self.update_pagination()
            page = self.pagination.current_page
            per_page = self.pagination.rows_per_page
            trace = trace[(page-1)*per_page:page*per_page]

        row_count = len(trace)
        self.setRowCount(row_count)
        if row_count == 0:
            return

        for i in range(0, row_count):
            row_id = str(trace[i]["id"])
            address = trace[i].get("ip")
            opcodes = trace[i]["opcodes"]
            disasm = trace[i]["disasm"]
            comment = str(trace[i]["comment"])
            comment_item = QTableWidgetItem(comment)
            comment_item.setWhatsThis("comment")
            row_id_item = QTableWidgetItem(row_id)
            row_id_item.setFlags(row_id_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(i, 0, row_id_item)
            if address is not None:
                self.setItem(i, 1, QTableWidgetItem(hex(address)))
            self.setItem(i, 2, QTableWidgetItem(opcodes))
            self.setItem(i, 3, QTableWidgetItem(disasm))
            self.setItem(i, 4, comment_item)

        self.itemChanged.connect(self.item_changed)

    def update_column_widths(self):
        """Updates column widths of a TableWidget to match the content"""
        self.setVisible(False)          # fix ui glitch with column widths
        self.resizeColumnsToContents()
        self.setColumnWidth(0, 64)      # make id column wider
        self.horizontalHeader().setStretchLastSection(True)
        self.setVisible(True)

    def update_pagination(self):
        if self.trace is not None:
            trace_length = len(self.trace)
            page_count = int(trace_length / self.pagination.rows_per_page) + 1
            self.pagination.set_page_count(page_count)
