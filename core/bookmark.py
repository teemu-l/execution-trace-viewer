class Bookmark:
    """Bookmark class for TraceData

    Attributes:
        addr (str): Address of startrow
        disasm (str): Disassembly of bookmark's startrow
        startrow (int): First row of bookmark (index in trace list)
        endrow (int): Last row of bookmark
        comment (str): Comment
    """
    def __init__(self, addr="", disasm="", startrow=0, endrow=0, comment=""):
        self.addr = addr
        self.disasm = disasm
        self.startrow = startrow
        self.endrow = endrow
        self.comment = comment
