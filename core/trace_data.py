from operator import attrgetter


class TraceData:
    """TraceData class.

    Class for storing execution trace and bookmarks.

    Attributes:
        filename (str): A trace file name.
        arch (str): CPU architecture.
        ip_reg (str): Name of instruction pointer register
        pointer_size (int): Pointer size (4 in x86, 8 in x64)
        regs (dict): Register names and indexes
        trace (list): A list of traced instructions, registers and memory accesses.
        bookmarks (list): A list of bookmarks.
    """

    def __init__(self):
        """Inits TraceData."""
        self.filename = ""
        self.arch = ""
        self.ip_reg = ""
        self.pointer_size = 0
        self.regs = {}
        self.trace = []
        self.bookmarks = []

    def clear(self):
        """Clears trace and all data"""
        self.trace = []
        self.bookmarks = []

    def get_trace(self):
        """Returns a full trace

        Returns:
            list: Trace
        """
        return self.trace

    def get_regs(self):
        """Returns dict of registers and their indexes

        Returns:
            dict: Regs
        """
        return self.regs

    def get_regs_and_values(self, row):
        """Returns dict of registers and their values

        Returns:
            dict: Register names and values
        """
        registers = {}
        try:
            reg_values = self.trace[row]["regs"]
            for reg_name, reg_index in self.regs.items():
                reg_value = reg_values[reg_index]
                registers[reg_name] = reg_value
        except IndexError:
            print(f"Error. Could not get regs from row {row}.")
            return {}
        return registers

    def get_reg_index(self, reg_name):
        """Returns a register index

        Args:
            reg_name (str): Register name
        Returns:
            int: Register index
        """
        try:
            index = self.regs[reg_name]
        except KeyError:
            print("Unknown register")
        return index

    def get_modified_regs(self, row):
        """Returns modfied regs

        Args:
            row (int): Trace row index
        Returns:
            list: List of register names
        """
        modified_regs = []
        reg_values = self.trace[row]["regs"]
        next_row = row + 1
        if next_row < len(self.trace):
            next_row_data = self.trace[next_row]
            for reg_name, reg_index in self.regs.items():
                reg_value = reg_values[reg_index]
                next_reg_value = next_row_data["regs"][reg_index]
                if next_reg_value != reg_value:
                    modified_regs.append(reg_name)
        return modified_regs

    def get_trace_rows(self, rows):
        """Returns a trace of given rows

        Args:
            rows (list): List of trace indexes
        Returns:
            list: Trace
        """
        trace = []
        try:
            trace = [self.trace[int(i)] for i in rows]
        except IndexError:
            print("Error. Could not get trace rows.")
        return trace

    def get_instruction_pointer_name(self):
        """Returns an instruction pointer name

        Returns:
            str: Instruction pointer name
        """
        if self.ip_reg:
            return self.ip_reg
        elif "eip" in self.regs:
            return "eip"
        elif "rip" in self.regs:
            return "rip"
        elif "ip" in self.regs:
            return "ip"
        elif "pc" in self.regs:
            return "pc"
        return ""

    def get_instruction_pointer(self, row):
        """Returns a value of instruction pointer of given row

        Args:
            row: A row index in trace
        Returns:
            int: Address of instruction
        """
        ip = 0
        ip_reg = self.get_instruction_pointer_name()
        try:
            reg_index = self.regs[ip_reg]
            ip = self.trace[row]["regs"][reg_index]
        except IndexError:
            print(f"Error. Could not get IP from row {row}")
        return ip

    def set_comment(self, row, comment):
        """Adds a comment to trace

        Args:
            row (int): Row index in trace
            comment (str): Comment text
        """
        try:
            self.trace[row]["comment"] = str(comment)
        except IndexError:
            print(f"Error. Could not set comment to row {row}")

    def add_bookmark(self, new_bookmark, replace=False):
        """Adds a new bookmark

        Args:
            new_bookmark (Bookmark): A new bookmark
            replace (bool): Replace an existing bookmark if found on same row?
                Defaults to False.
        """
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.startrow == new_bookmark.startrow:
                if replace:
                    self.bookmarks[i] = new_bookmark
                    print(f"Bookmark at {bookmark.startrow} replaced.")
                else:
                    print(f"Error: bookmark at {bookmark.startrow} already exists.")
                return
        self.bookmarks.append(new_bookmark)
        self.sort_bookmarks()

    def delete_bookmark(self, index):
        """Deletes a bookmark

        Args:
            index (int): Index on bookmark list
        Returns:
            bool: True if bookmark deleted, False otherwise
        """
        try:
            del self.bookmarks[index]
        except IndexError:
            print(f"Error. Could not delete a bookmark {index}")
            return False
        return True

    def sort_bookmarks(self):
        """Sorts bookmarks by startrow"""
        self.bookmarks.sort(key=attrgetter("startrow"))

    def get_bookmark_from_row(self, row):
        """Returns a bookmark for a given trace row.

        Args:
            row (int): Trace row index
        Returns:
            Bookmark: Returns A Bookmark if found, None otherwise.
        """
        for bookmark in self.bookmarks:
            if bookmark.startrow <= row <= bookmark.endrow:
                return bookmark
        return None

    def get_bookmarks(self):
        """Returns all bookmarks

        Returns:
            list: List of bookmarks
        """
        return self.bookmarks

    def set_bookmarks(self, bookmarks):
        """Sets bookmarks

        Args:
            bookmarks (list): Bookmarks
        """
        self.bookmarks = bookmarks

    def clear_bookmarks(self):
        """Clears bookmarks"""
        self.bookmarks = []
