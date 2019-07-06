PACKAGE_NAME = "Execution Trace Viewer"
PACKAGE_AUTHOR = "Teemu Laurila"
PACKAGE_URL = "https://github.com/teemu-l/execution-trace-viewer"
PACKAGE_VERSION = "1.0.0"
PACKAGE_COPYRIGHTS = "(C) 2019 Teemu Laurila"

DEBUG = True
STYLE = "Fusion"
USE_DARK_THEME = True
HIGHLIGHT_MODIFIED_REGS = True
USE_SYNTAX_HIGHLIGHT = True
SHOW_SAMPLE_FILTERS = True
SAMPLE_FILTERS = [
    "",
    "disasm=push|pop",
    "reg_eax=0x1",
    "reg_any=0x1",
    "rows=0-200",
    "regex=0x40?00",
    "iregex=junk|decrypt",
    "mem_value=0x1",
    "mem_read_value=0x1",
    "mem_write_value=0x1",
    "mem_addr=0x4f20",
    "mem_read_addr=0x4f20",
    "mem_write_addr=0x4f20",
    "opcodes=c704",
    "comment=decrypt"
]

FIND_FIELDS = ["Disasm", "Regs", "Memory a/v", "Mem address", "Mem value", "Comment", "Any"]

# columns for tables
TRACE_LABELS = ["#", "address", "opcodes", "disasm", "comment"]
BOOKMARK_LABELS = ["start row", "end row", "addr", "disasm", "comment"]
REG_LABELS = ["reg", "hex", "dec"]
MEM_LABELS = ["access", "address", "value"]

PAGINATION_ENABLED = True
PAGINATION_ROWS_PER_PAGE = 10000

# ask for comment when creating a bookmark?
ASK_FOR_BOOKMARK_COMMENT = True

# registers for x64dbg traces
# if you want to see more regs, add them here (in correct order)
# check the order of regs from REGISTERCONTEXT:
# https://github.com/x64dbg/x64dbg/blob/development/src/bridge/bridgemain.h#L723
X32_REGS = [
    "eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi",
    "eip", "eflags", "gs", "fs", "es", "ds", "cs", "ss",
    "dr0", "dr1", "dr2", "dr3", "dr6", "dr7"
]
X64_REGS = [
    "rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi",
    "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
    "rip", "eflags", "gs", "fs", "es", "ds", "cs", "ss",
    "dr0", "dr1", "dr2", "dr3", "dr6", "dr7"
]

# disable this to show all registers
REG_FILTER_ENABLED = True

# regs not on this list are filtered out of reglist
REG_FILTER = [
    "eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi", "eip",
    "rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi",
    "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "rip",
    "eflags",
    # "gs","fs","es","ds","cs","ss",
    "dr0", "dr1", "dr2", "dr3", "dr6", "dr7",
]
