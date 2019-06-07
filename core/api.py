
class Api:
    """Api class for plugins

    Attributes:
        main_window (QMainWindow): main_window object
    """
    def __init__(self, main_window):
        """Inits Api."""
        self.main_window = main_window

    def ask_user(self, title, question):
        """Shows a messagebox with yes/no question

        Args:
            title (str): MessageBox title
            question (str): MessageBox qustion label
        Returns:
            bool: True if user clicked yes, False otherwise
        """
        return self.main_window.ask_user(title, question)

    def get_bookmarks(self):
        """Returns all bookmarks

        Returns:
            list: bookmarks
        """
        return self.main_window.trace_data.get_bookmarks()

    def get_filtered_trace(self):
        """Returns filtered_trace"""
        return self.main_window.filtered_trace

    def get_full_trace(self):
        """Returns full trace from TraceData object"""
        return self.main_window.trace_data.trace

    def get_main_window(self):
        """Returns main_window object"""
        return self.main_window

    def get_selected_trace(self):
        """Returns list of selected trace"""
        row_ids = self.get_selected_trace_row_ids()
        trace_data = self.get_trace_data()
        trace = trace_data.get_trace_rows(row_ids)
        return trace

    def get_string_from_user(self, title, label):
        """Get string from user.

        Args:
            title (str): Input dialog title
            label (str): Input dialog label
        Returns:
            string: String given by user, None if user clicked No
        """
        return self.main_window.get_string_from_user(title, label)

    def get_values_from_user(self, title, label):
        """Get integer values from user. Values must be separated by comma.
        If any value starts with '0x', it is converted from hex to decimal.

        Args:
            title (str): Input dialog title
            label (str): Input dialog label
        Returns:
            list: list of integers, None if wrong or no values given.
        """
        values_str = self.main_window.get_string_from_user(
            title, label
        )
        if values_str:
            values = []
            for value in values_str.split(','):
                if value.startswith('0x'):
                    values.append(int(value, 16))
                else:
                    values.append(int(value))
            return values
        return None

    def get_selected_bookmarks(self):
        """Returns list of selected bookmarks"""
        return self.main_window.get_selected_bookmarks()

    def get_selected_trace_row_ids(self):
        """Returns list of ids of selected rows"""
        return self.main_window.get_selected_row_ids(self.main_window.trace_table)

    def get_trace_data(self):
        """Returns TraceData object"""
        return self.main_window.trace_data

    def get_visible_trace(self):
        """Returns visible trace, either full or filtered trace"""
        return self.main_window.get_visible_trace()

    def print(self, text):
        """Prints text to log"""
        self.main_window.print(str(text))

    def set_filtered_trace(self, trace):
        """Sets filtered_trace"""
        self.main_window.filtered_trace = trace

    def show_filtered_trace(self):
        """Shows filtered trace on trace_table"""
        self.main_window.show_filtered_trace()

    def show_messagebox(self, text):
        """Shows a messagebox"""
        self.main_window.show_messagebox(text)

    def update_trace_table(self):
        """Updates trace_table"""
        self.main_window.update_trace_table()

    def update_bookmark_table(self):
        """Updates bookmark_table"""
        self.main_window.update_bookmark_table()
