from operator import attrgetter


class TraceData:
    """TraceData class.

    Class for storing execution traces and bookmarks.

    Attributes:
        filename (str): A trace file name.
        arch (str): CPU architecture.
        ip_name (str): Instruction pointer name
        regs (dict): Register names and indexes
        trace (list): A list of traced instructions, registers and memory accesses.
        bookmarks (list): A list of bookmarks.
    """

    def __init__(self):
        """Inits TraceData."""
        self.filename = ""
        self.arch = ""
        self.ip_name = ""
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
            print('Unknown register')
        return index

    def get_modified_regs(self, row):
        """Returns modfied regs

        Args:
            row (int): Trace row index
        Returns:
            list: List of register names
        """
        modfied_regs = []
        reg_values = self.trace[row]["regs"]
        next_row = row + 1
        if next_row < len(self.trace):
            for reg_name, reg_index in self.regs.items():
                reg_value = reg_values[reg_index]
                next_row_data = self.trace[next_row]
                next_reg_value = next_row_data["regs"][reg_index]
                if next_reg_value != reg_value:
                    modfied_regs.append(reg_name)
        return modfied_regs

    def get_trace_rows(self, rows):
        """Returns a trace of specified rows

        Args:
            rows (list): List of trace indexes
        Returns:
            list: Trace
        """
        trace = []
        try:
            for index in rows:
                trace.append(self.trace[int(index)])
        except IndexError:
            print("Error. Could not get trace rows.")
        return trace

    def get_instruction_pointer_name(self):
        """Returns an instruction pointer name

        Returns:
            str: Instruction pointer name
        """
        if self.ip_name:
            return self.ip_name
        ip_name = ""
        try:
            if "eip" in self.regs:
                ip_name = "eip"
            elif "rip" in self.regs:
                ip_name = "rip"
            elif "ip" in self.regs:
                ip_name = "ip"
        except IndexError:
            print("Error. Could not get IP name")
        return ip_name

    def get_instruction_pointer(self, row):
        """Returns a value of instruction pointer of specified row

        Args:
            row: Trace index
        Returns:
            int: Address of instruction
        """
        ip = 0
        try:
            ip_name = self.get_instruction_pointer_name()
            reg_index = self.regs[ip_name]
            ip = self.trace[row]["regs"][reg_index]
            # if ip_name in regs:
            #     ip = regs[ip_name]
        except IndexError:
            print("Error. Could not get IP from row " + str(row))
        return ip

    def set_comment(self, comment, row):
        """Adds a comment to trace

        Args:
            comment (str): Comment text
            row (int): Trace index
        """
        try:
            self.trace[row]["comment"] = str(comment)
        except IndexError:
            print("Error. Could not set comment to row " + str(row))

    def add_bookmark(self, new_bookmark, replace=False):
        """Adds a new bookmark

        Args:
            new_bookmark (Bookmark): A new bookmark
            replace (bool): Replace an existing bookmark if found on same row?
                Defaults to False.
        """
        for i, bookmark in enumerate(self.bookmarks):
            if self.bookmarks[i].startrow == new_bookmark.startrow:
                if replace:
                    self.bookmarks[i] = new_bookmark
                    print("Bookmark at %s replaced." % bookmark.startrow)
                else:
                    print("Error: bookmark at %s already exists." % bookmark.startrow)
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
            print("Error. Could not delete a bookmark " + str(index))
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
