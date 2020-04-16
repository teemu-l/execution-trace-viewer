import sys
import os
import functools
import traceback

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QMenu,
    QFileDialog,
    QAbstractItemView,
    QMessageBox,
    QInputDialog,
    QLineEdit,
    QTableWidgetItem,
    QApplication,
)
from yapsy.PluginManager import PluginManager

from core.trace_data import TraceData
from core import trace_files
from core.filter_and_find import find
from core.filter_and_find import filter_trace
from core.filter_and_find import TraceField
from core.api import Api
from core import prefs
from gui.syntax_hl.syntax_hl_log import AsmHighlighter
from gui.widgets.pagination_widget import PaginationWidget
from gui.widgets.find_widget import FindWidget
from gui.widgets.filter_widget import FilterWidget
from gui.input_dialog import InputDialog


class MainWindow(QMainWindow):
    """MainWindow class

    Attributes:
        trace_data (TraceData): TraceData object
        filtered_trace (list): Filtered trace
    """

    def __init__(self, parent=None):
        """Inits MainWindow, UI and plugins"""
        super(MainWindow, self).__init__(parent)
        self.api = Api(self)
        self.trace_data = TraceData()
        self.filtered_trace = []
        self.init_plugins()
        self.init_ui()
        if len(sys.argv) > 1:
            self.open_trace(sys.argv[1])

    def dragEnterEvent(self, event):
        """QMainWindow method reimplementation for file drag."""
        event.setDropAction(Qt.MoveAction)
        super().dragEnterEvent(event)
        event.accept()

    def dropEvent(self, event):
        """QMainWindow method reimplementation for file drop."""
        super().dropEvent(event)
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_file = url.toLocalFile()
                if os.path.isfile(local_file):
                    self.open_trace(local_file)

    def init_ui(self):
        """Inits UI"""
        uic.loadUi("gui/mainwindow.ui", self)

        title = prefs.PACKAGE_NAME + " " + prefs.PACKAGE_VERSION
        self.setWindowTitle(title)

        # accept file drops
        self.setAcceptDrops(True)

        # make trace table wider than regs&mem
        self.splitter1.setSizes([1400, 100])
        self.splitter2.setSizes([600, 100])

        # Init trace table
        self.trace_table.itemSelectionChanged.connect(self.on_trace_table_row_changed)
        self.trace_table.setColumnCount(len(prefs.TRACE_LABELS))
        self.trace_table.setHorizontalHeaderLabels(prefs.TRACE_LABELS)
        self.trace_table.horizontalHeader().setStretchLastSection(True)
        self.trace_table.bookmarkCreated.connect(self.add_bookmark)
        self.trace_table.commentEdited.connect(self.set_comment)
        self.trace_table.printer = self.print

        if prefs.USE_SYNTAX_HIGHLIGHT_IN_TRACE:
            dark_text = False
            if not prefs.USE_DARK_THEME:
                dark_text = True
            self.trace_table.init_syntax_highlight(dark_text)

        # trace pagination
        if prefs.PAGINATION_ENABLED:
            self.trace_pagination = PaginationWidget()
            self.trace_pagination.pageChanged.connect(self.trace_table.update)
            self.horizontalLayout.addWidget(self.trace_pagination)
            self.trace_pagination.set_enabled(True)
            self.trace_pagination.rows_per_page = prefs.PAGINATION_ROWS_PER_PAGE

            self.trace_table.pagination = self.trace_pagination
            self.horizontalLayout.setAlignment(self.trace_pagination, Qt.AlignLeft)

        # these are used to remember current pages & scroll values for both traces
        self.trace_current_pages = [1, 1]
        self.trace_scroll_values = [0, 0]

        self.reg_table.setColumnCount(len(prefs.REG_LABELS))
        self.reg_table.setHorizontalHeaderLabels(prefs.REG_LABELS)
        self.reg_table.horizontalHeader().setStretchLastSection(True)

        if prefs.REG_FILTER_ENABLED:
            self.reg_table.filtered_regs = prefs.REG_FILTER

        # Init memory table
        self.mem_table.setColumnCount(len(prefs.MEM_LABELS))
        self.mem_table.setHorizontalHeaderLabels(prefs.MEM_LABELS)
        self.mem_table.horizontalHeader().setStretchLastSection(True)

        # Init bookmark table
        self.bookmark_table.setColumnCount(len(prefs.BOOKMARK_LABELS))
        self.bookmark_table.setHorizontalHeaderLabels(prefs.BOOKMARK_LABELS)
        self.bookmark_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bookmark_table.customContextMenuRequested.connect(
            self.bookmark_table_context_menu_event
        )

        self.bookmark_menu = QMenu(self)

        go_action = QAction("Go to bookmark", self)
        go_action.triggered.connect(self.go_to_bookmark_in_trace)
        self.bookmark_menu.addAction(go_action)

        delete_bookmarks_action = QAction("Delete bookmark(s)", self)
        delete_bookmarks_action.triggered.connect(self.delete_bookmarks)
        self.bookmark_menu.addAction(delete_bookmarks_action)

        # Menu
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)

        open_trace_action = QAction("&Open trace..", self)
        open_trace_action.setStatusTip("Open trace")
        open_trace_action.triggered.connect(self.dialog_open_trace)

        self.save_trace_action = QAction("&Save trace", self)
        self.save_trace_action.setStatusTip("Save trace")
        self.save_trace_action.triggered.connect(self.save_trace)
        self.save_trace_action.setEnabled(False)

        save_trace_as_action = QAction("&Save trace as..", self)
        save_trace_as_action.setStatusTip("Save trace as..")
        save_trace_as_action.triggered.connect(self.dialog_save_trace_as)

        save_trace_as_json_action = QAction("&Save trace as JSON..", self)
        save_trace_as_json_action.setStatusTip("Save trace as JSON..")
        save_trace_as_json_action.triggered.connect(self.dialog_save_trace_as_json)

        file_menu = self.menu_bar.addMenu("&File")
        file_menu.addAction(open_trace_action)
        file_menu.addAction(self.save_trace_action)
        file_menu.addAction(save_trace_as_action)
        file_menu.addAction(save_trace_as_json_action)
        file_menu.addAction(exit_action)

        self.plugins_topmenu = self.menu_bar.addMenu("&Plugins")

        clear_bookmarks_action = QAction("&Clear bookmarks", self)
        clear_bookmarks_action.setStatusTip("Clear bookmarks")
        clear_bookmarks_action.triggered.connect(self.clear_bookmarks)

        bookmarks_menu = self.menu_bar.addMenu("&Bookmarks")
        bookmarks_menu.addAction(clear_bookmarks_action)

        # Init right click menu for trace table
        self.init_trace_table_menu()
        # Init plugins menu on menu bar
        self.init_plugins_menu()

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)

        about_menu = self.menu_bar.addMenu("&About")
        about_menu.addAction(about_action)

        if prefs.USE_SYNTAX_HIGHLIGHT_IN_LOG:
            self.highlight = AsmHighlighter(self.log_text_edit.document())

        # trace select
        self.select_trace_combo_box.addItem("Full trace")
        self.select_trace_combo_box.addItem("Filtered trace")
        self.select_trace_combo_box.currentIndexChanged.connect(
            self.trace_combo_box_index_changed
        )

        self.filter_widget = FilterWidget()
        self.filter_widget.filterBtnClicked.connect(self.on_filter_btn_clicked)
        self.horizontalLayout.addWidget(self.filter_widget)
        if prefs.SHOW_SAMPLE_FILTERS:
            self.filter_widget.set_sample_filters(prefs.SAMPLE_FILTERS)

        self.find_widget = FindWidget()
        self.find_widget.findBtnClicked.connect(self.on_find_btn_clicked)
        self.find_widget.set_fields(prefs.FIND_FIELDS)
        self.horizontalLayout.addWidget(self.find_widget)

        self.show()

    def init_plugins(self):
        """Inits plugins"""
        self.manager = PluginManager()
        self.manager.setPluginPlaces(["plugins"])
        self.manager.collectPlugins()
        for plugin in self.manager.getAllPlugins():
            print_debug(f"Plugin found: {plugin.name}")

    def init_plugins_menu(self):
        """Inits plugins menu"""
        self.plugins_topmenu.clear()

        reload_action = QAction("Reload plugins", self)
        reload_action.setShortcut("Ctrl+R")
        func = functools.partial(self.reload_plugins)
        reload_action.triggered.connect(func)
        self.plugins_topmenu.addAction(reload_action)
        self.plugins_topmenu.addSeparator()

        plugins_menu = QMenu("Run plugin", self)

        for plugin in self.manager.getAllPlugins():
            action = QAction(plugin.name, self)
            func = functools.partial(self.execute_plugin, plugin)
            action.triggered.connect(func)
            plugins_menu.addAction(action)
        self.plugins_topmenu.addMenu(plugins_menu)

    def init_trace_table_menu(self):
        """Initializes right click menu for trace table"""
        self.trace_table_menu = QMenu(self)

        copy_action = QAction("Print selected cells", self)
        copy_action.triggered.connect(self.trace_table.print_selected_cells)
        self.trace_table_menu.addAction(copy_action)

        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.trace_table.create_bookmark)
        self.trace_table_menu.addAction(add_bookmark_action)

        plugins_menu = QMenu("Plugins", self)

        for plugin in self.manager.getAllPlugins():
            action = QAction(plugin.name, self)
            func = functools.partial(self.execute_plugin, plugin)
            action.triggered.connect(func)
            plugins_menu.addAction(action)
        self.trace_table_menu.addMenu(plugins_menu)
        self.trace_table.menu = self.trace_table_menu

    def reload_plugins(self):
        """Reloads plugins"""
        self.init_plugins()
        self.init_trace_table_menu()
        self.init_plugins_menu()

    def on_trace_table_row_changed(self):
        """Called when selected row changes"""
        selected_row_ids = self.get_selected_row_ids(self.trace_table)
        if not selected_row_ids:
            return
        row_id = selected_row_ids[0]
        regs = self.trace_data.get_regs_and_values(row_id)
        modified_regs = []
        if prefs.HIGHLIGHT_MODIFIED_REGS:
            modified_regs = self.trace_data.get_modified_regs(row_id)
        self.reg_table.set_data(regs, modified_regs)
        mem = []
        if "mem" in self.trace_data.trace[row_id]:
            mem = self.trace_data.trace[row_id]["mem"]
        self.mem_table.set_data(mem)
        self.update_status_bar()

    def on_filter_btn_clicked(self, filter_text: str):
        if self.trace_data is None:
            return
        try:
            filtered_trace = filter_trace(
                self.trace_data.trace,  # get_visible_trace(),
                self.trace_data.get_regs(),
                filter_text,
            )
        except Exception as exc:
            self.show_messagebox("Filter error", f"{exc}")
            # print(traceback.format_exc())
        else:
            self.filtered_trace = filtered_trace
            self.show_filtered_trace()

    def on_find_btn_clicked(self, keyword: str, field_index: int, direction: int):
        """Find next or prev button clicked"""
        current_row = self.trace_table.currentRow()
        if current_row < 0:
            current_row = 0

        if self.trace_table.pagination is not None:
            pagination = self.trace_table.pagination
            page = pagination.current_page
            rows_per_page = pagination.rows_per_page
            current_row += (page - 1) * rows_per_page

        if field_index == 0:
            field = TraceField.DISASM
        elif field_index == 1:
            field = TraceField.REGS
        elif field_index == 2:
            field = TraceField.MEM
        elif field_index == 3:
            field = TraceField.MEM_ADDR
        elif field_index == 4:
            field = TraceField.MEM_VALUE
        elif field_index == 5:
            field = TraceField.COMMENT
        elif field_index == 6:
            field = TraceField.ANY

        try:
            row_number = find(
                trace=self.get_visible_trace(),
                field=field,
                keyword=keyword,
                start_row=current_row + direction,
                direction=direction,
            )
        except Exception as exc:
            self.show_messagebox("Find error", f"{exc}")
            print(traceback.format_exc())
            self.print(traceback.format_exc())
            return

        if row_number is not None:
            self.trace_table.go_to_row(row_number)
        else:
            print_debug(
                f"{keyword} not found (row: {current_row}, direction: {direction})"
            )

    def get_visible_trace(self):
        """Returns the trace that is currently shown on trace table"""
        index = self.select_trace_combo_box.currentIndex()
        if self.trace_data is not None:
            if index == 0:
                return self.trace_data.trace
            else:
                return self.filtered_trace
        return None

    def bookmark_table_context_menu_event(self):
        """Context menu for bookmark table right click"""
        self.bookmark_menu.popup(QCursor.pos())

    def dialog_open_trace(self):
        """Shows dialog to open trace file"""
        all_traces = "All traces (*.tvt *.trace32 *.trace64)"
        all_files = "All files (*.*)"
        filename = QFileDialog.getOpenFileName(
            self, "Open trace", "", all_traces + ";; " + all_files
        )[0]
        if filename:
            self.open_trace(filename)
            if self.trace_data:
                self.save_trace_action.setEnabled(True)

    def dialog_save_trace_as(self):
        """Shows a dialog to select a save file"""
        filename = QFileDialog.getSaveFileName(
            self, "Save trace as", "", "Trace Viewer traces (*.tvt);; All files (*.*)"
        )[0]
        print_debug("Save trace as: " + filename)
        if filename and trace_files.save_as_tv_trace(self.trace_data, filename):
            self.trace_data.filename = filename
            self.save_trace_action.setEnabled(True)

    def dialog_save_trace_as_json(self):
        """Shows a dialog to save trace to JSON file"""
        filename = QFileDialog.getSaveFileName(
            self, "Save as JSON", "", "JSON files (*.txt);; All files (*.*)"
        )[0]
        print_debug("Save trace as: " + filename)
        if filename:
            trace_files.save_as_json(self.trace_data, filename)

    def execute_plugin(self, plugin):
        """Executes a plugin and updates tables"""
        print_debug(f"Executing a plugin: {plugin.name}")
        try:
            plugin.plugin_object.execute(self.api)
        except Exception:
            print("Error in plugin:")
            print(traceback.format_exc())
            self.print("Error in plugin:")
            self.print(traceback.format_exc())
        finally:
            if prefs.USE_SYNTAX_HIGHLIGHT_IN_LOG:
                self.highlight.rehighlight()

    def show_filtered_trace(self):
        """Shows filtered_trace on trace_table"""
        if self.select_trace_combo_box.currentIndex() == 0:
            self.select_trace_combo_box.setCurrentIndex(1)
        else:
            self.trace_table.set_data(self.filtered_trace)
            self.trace_table.update()

    def set_comment(self, row_id, comment):
        """Sets comment to row on full trace"""
        self.trace_data.set_comment(row_id, comment)

    def on_bookmark_table_cell_edited(self, item):
        """Called when any cell is edited on bookmark table"""
        cell_type = item.whatsThis()
        bookmarks = self.trace_data.get_bookmarks()
        row = self.bookmark_table.currentRow()
        if row < 0:
            print_debug("Error, could not edit bookmark.")
            return
        if cell_type == "startrow":
            bookmarks[row].startrow = int(item.text())
        elif cell_type == "endrow":
            bookmarks[row].endrow = int(item.text())
        elif cell_type == "address":
            bookmarks[row].addr = item.text()
        elif cell_type == "disasm":
            bookmarks[row].disasm = item.text()
        elif cell_type == "comment":
            bookmarks[row].comment = item.text()
        else:
            print_debug("Unknown field edited on bookmark table...")

    def open_trace(self, filename):
        """Opens and reads a trace file"""
        print_debug(f"Opening trace file: {filename}")
        self.close_trace()
        self.trace_data = trace_files.open_trace(filename)
        if self.trace_data is None:
            print_debug(f"Error, couldn't open trace file: {filename}")
        else:
            if prefs.PAGINATION_ENABLED:
                self.trace_pagination.set_current_page(1, True)
            self.trace_table.set_data(self.trace_data.trace)
            self.trace_table.update()
        self.update_bookmark_table()
        self.trace_table.update_column_widths()

    def close_trace(self):
        """Clears trace and updates UI"""
        self.trace_data = None
        self.filtered_trace = []
        self.trace_table.set_data([])
        self.update_ui()

    def update_ui(self):
        """Updates tables and status bar"""
        self.trace_table.update()
        self.update_bookmark_table()
        self.update_status_bar()

    def save_trace(self):
        """Saves a trace file"""
        filename = self.trace_data.filename
        print_debug("Save trace: " + filename)
        if filename:
            trace_files.save_as_tv_trace(self.trace_data, filename)

    def show_about_dialog(self):
        """Shows an about dialog"""
        title = "About"
        name = prefs.PACKAGE_NAME
        version = prefs.PACKAGE_VERSION
        copyrights = prefs.PACKAGE_COPYRIGHTS
        url = prefs.PACKAGE_URL
        text = f"{name} {version} \n {copyrights} \n {url}"
        QMessageBox().about(self, title, text)

    def update_column_widths(self, table):
        """Updates column widths of a TableWidget to match the content"""
        table.setVisible(False)  # fix ui glitch with column widths
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        table.setVisible(True)

    def update_status_bar(self):
        """Updates status bar"""
        if self.trace_data is None:
            return
        table = self.trace_table
        row = table.currentRow()

        row_count = table.rowCount()
        row_info = f"{row}/{row_count - 1}"
        filename = self.trace_data.filename.split("/")[-1]
        msg = f"File: {filename} | Row: {row_info} "

        selected_row_id = 0
        row_ids = self.trace_table.get_selected_row_ids()
        if row_ids:
            selected_row_id = row_ids[0]

        msg += f" | {len(self.trace_data.trace)} rows in full trace."
        msg += f" | {len(self.filtered_trace)} rows in filtered trace."

        bookmark = self.trace_data.get_bookmark_from_row(selected_row_id)
        if bookmark:
            msg += f" | Bookmark: {bookmark.disasm}   ; {bookmark.comment}"

        self.status_bar.showMessage(msg)

    def get_selected_row_ids(self, table):
        """Returns IDs of all selected rows of TableWidget.

        Args:
            table: PyQt TableWidget
        returns:
            list: Ordered list of row ids
        """
        # use a set so we don't get duplicate ids
        row_ids_set = set(
            table.item(index.row(), 0).text() for index in table.selectedIndexes()
        )
        try:
            row_ids_list = [int(i) for i in row_ids_set]
        except ValueError:
            print_debug("Error. Values in the first column must be integers.")
            return []
        return sorted(row_ids_list)

    def trace_combo_box_index_changed(self, index):
        """Trace selection combo box index changed"""
        self.trace_table.set_data(self.get_visible_trace())

        other_index = index ^ 1
        if prefs.PAGINATION_ENABLED:
            # save current page
            self.trace_current_pages[other_index] = self.trace_pagination.current_page
            self.trace_pagination.set_current_page(
                self.trace_current_pages[index], True
            )

        # save scrollbar value
        current_scroll = self.trace_table.verticalScrollBar().value()
        self.trace_scroll_values[other_index] = current_scroll
        next_value = self.trace_scroll_values[index]

        self.trace_table.update()
        QApplication.processEvents()  # this is needed to update the scrollbar
        self.trace_table.verticalScrollBar().setValue(next_value)

    def go_to_row_in_visible_trace(self, row):
        """Goes to given row in currently visible trace"""
        self.trace_table.go_to_row(row)
        self.tab_widget.setCurrentIndex(0)

    def go_to_row_in_full_trace(self, row_id):
        """Switches to full trace and goes to given row"""
        # make sure we are shown full trace, not filtered
        if self.select_trace_combo_box.currentIndex() == 1:
            self.select_trace_combo_box.setCurrentIndex(0)
        self.go_to_row_in_visible_trace(row_id)

    def go_to_bookmark_in_trace(self):
        """Goes to trace row of selected bookmark"""
        selected_row_ids = self.get_selected_row_ids(self.bookmark_table)
        if not selected_row_ids:
            print_debug("Error. No bookmark selected.")
            return
        self.go_to_row_in_full_trace(selected_row_ids[0])

    def clear_bookmarks(self):
        """Clears all bookmarks"""
        self.trace_data.clear_bookmarks()
        self.update_bookmark_table()

    def delete_bookmarks(self):
        """Deletes selected bookmarks"""
        selected = self.bookmark_table.selectedItems()
        if not selected:
            print_debug("Could not delete a bookmark. Nothing selected.")
            return
        selected_rows = sorted(set({sel.row() for sel in selected}))
        for row in reversed(selected_rows):
            self.trace_data.delete_bookmark(row)
            self.bookmark_table.removeRow(row)

    def get_selected_bookmarks(self):
        """Returns selected bookmarks"""
        selected = self.bookmark_table.selectedItems()
        if not selected:
            print_debug("No bookmarks selected.")
            return []
        selected_rows = sorted(set({sel.row() for sel in selected}))
        all_bookmarks = self.trace_data.get_bookmarks()
        return [all_bookmarks[i] for i in selected_rows]

    def add_bookmark(self, bookmark):
        if prefs.ASK_FOR_BOOKMARK_COMMENT:
            comment = self.get_string_from_user(
                "Bookmark comment", "Give a comment for bookmark:"
            )
            if comment:
                bookmark.comment = comment
        self.trace_data.add_bookmark(bookmark)
        self.update_bookmark_table()

    def update_bookmark_table(self):
        """Updates bookmarks table from trace_data"""
        if self.trace_data is None:
            return
        table = self.bookmark_table
        try:
            table.itemChanged.disconnect()
        except Exception:
            pass
        bookmarks = self.trace_data.get_bookmarks()
        table.setRowCount(len(bookmarks))

        for i, bookmark in enumerate(bookmarks):
            startrow = QTableWidgetItem(bookmark.startrow)
            startrow.setData(Qt.DisplayRole, int(bookmark.startrow))
            startrow.setWhatsThis("startrow")
            table.setItem(i, 0, startrow)

            endrow = QTableWidgetItem(bookmark.endrow)
            endrow.setData(Qt.DisplayRole, int(bookmark.endrow))
            endrow.setWhatsThis("endrow")
            table.setItem(i, 1, endrow)

            address = QTableWidgetItem(bookmark.addr)
            address.setWhatsThis("address")
            table.setItem(i, 2, address)

            disasm = QTableWidgetItem(bookmark.disasm)
            disasm.setWhatsThis("disasm")
            table.setItem(i, 3, disasm)

            comment = QTableWidgetItem(bookmark.comment)
            comment.setWhatsThis("comment")
            table.setItem(i, 4, comment)

        table.itemChanged.connect(self.on_bookmark_table_cell_edited)
        self.update_column_widths(table)

    def print(self, text):
        """Prints text to TextEdit on log tab"""
        self.log_text_edit.appendPlainText(str(text))

    def go_to_row(self, table, row):
        """Scrolls a table to the specified row"""
        table.scrollToItem(table.item(row, 3), QAbstractItemView.PositionAtCenter)

    def ask_user(self, title, question):
        """Shows a messagebox with yes/no question

        Args:
            title (str): MessageBox title
            question (str): MessageBox qustion label
        Returns:
            bool: True if user clicked yes, False otherwise
        """
        answer = QMessageBox.question(
            self,
            title,
            question,
            QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No),
        )
        return bool(answer == QMessageBox.Yes)

    def get_string_from_user(self, title, label):
        """Gets a string from user

        Args:
            title (str): Input dialog title
            label (str): Input dialog label
        Returns:
            string: String given by user, empty string if user clicked cancel
        """
        answer, ok_clicked = QInputDialog.getText(
            self, title, label, QLineEdit.Normal, ""
        )
        if ok_clicked:
            return answer
        return ""

    def get_values_from_user(self, title, data, on_ok_clicked=None):
        """Gets values from user

        Args:
            title (str): Input dialog title
            data (list): List of dicts
            on_ok_clicked (method): Callback function to e.g. check the input
        Returns:
            list: List of values given by user, empty list if user canceled
        """
        input_dlg = InputDialog(self, title, data, on_ok_clicked)
        input_dlg.exec_()
        return input_dlg.get_data()

    def show_messagebox(self, title, msg):
        """Shows a messagebox"""
        alert = QMessageBox()
        alert.setWindowTitle(title)
        alert.setText(msg)
        alert.exec_()


def print_debug(msg):
    """Prints a debug message"""
    if prefs.DEBUG:
        print(msg)
