PACKAGE_NAME = "Execution Trace Viewer"
PACKAGE_AUTHOR = "Teemu Laurila"
PACKAGE_URL = "https://github.com/teemu-l/execution-trace-viewer"
PACKAGE_VERSION = "1.0.0"
PACKAGE_COPYRIGHTS = "(C) 2019 Teemu Laurila"

DEBUG = True

LIGHT_THEME = "Fusion"
USE_DARK_THEME = False

HIGHLIGHT_MODIFIED_REGS = True
USE_SYNTAX_HIGHLIGHT_IN_TRACE = True
USE_SYNTAX_HIGHLIGHT_IN_LOG = True
HL_REGS_X86 = {
    "r8": ["r8d", "r8w", "r8b"],
    "r9": ["r9d", "r9w", "r9b"],
    "r10": ["r10d", "r10w", "r10b"],
    "r11": ["r11d", "r11w", "r11b"],
    "r12": ["r12d", "r12w", "r12b"],
    "r13": ["r13d", "r13w", "r13b"],
    "r14": ["r14d", "r14w", "r14b"],
    "r15": ["r15d", "r15w", "r15b"],
}
HL_REGS_X86.update(dict.fromkeys(["rax", "eax"], ["rax", "eax", "ax", "ah", "al"]))
HL_REGS_X86.update(dict.fromkeys(["rbx", "ebx"], ["rbx", "ebx", "bx", "bh", "bl"]))
HL_REGS_X86.update(dict.fromkeys(["rcx", "ecx"], ["rcx", "ecx", "cx", "ch", "cl"]))
HL_REGS_X86.update(dict.fromkeys(["rdx", "edx"], ["rdx", "edx", "dx", "dh", "dl"]))
HL_REGS_X86.update(dict.fromkeys(["rbp", "ebp"], ["rbp", "ebp", "bp", "bpl"]))
HL_REGS_X86.update(dict.fromkeys(["rsi", "esi"], ["rsi", "esi", "si", "sil"]))
HL_REGS_X86.update(dict.fromkeys(["rdi", "edi"], ["rdi", "edi", "di", "dil"]))
HL_REGS_X86.update(dict.fromkeys(["rip", "eip"], ["rip", "eip", "ip"]))
HL_REGS_X86.update(dict.fromkeys(["rsp", "esp"], ["rsp", "esp", "sp", "spl"]))


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
    "comment=decrypt",
]

FIND_FIELDS = [
    "Disasm",
    "Registers",
    "Mem (any field)",
    "Mem address",
    "Mem value",
    "Comment",
    "Any",
]

# columns for tables
TRACE_LABELS = ["#", "address", "opcodes", "disasm", "comment"]
BOOKMARK_LABELS = ["start row", "end row", "addr", "disasm", "comment"]
REG_LABELS = ["reg", "hex", "dec"]
MEM_LABELS = ["access", "address", "value"]

TRACE_ROW_HEIGHT = 20

PAGINATION_ENABLED = True
PAGINATION_ROWS_PER_PAGE = 10000

# ask for comment when creating a bookmark?
ASK_FOR_BOOKMARK_COMMENT = True

# registers for x64dbg traces
# if you want to see more regs, add them here (in correct order)
# check the order of regs from REGISTERCONTEXT:
# https://github.com/x64dbg/x64dbg/blob/development/src/bridge/bridgemain.h#L723
X32_REGS = [
    "eax",
    "ecx",
    "edx",
    "ebx",
    "esp",
    "ebp",
    "esi",
    "edi",
    "eip",
    "eflags",
    "gs",
    "fs",
    "es",
    "ds",
    "cs",
    "ss",
    "dr0",
    "dr1",
    "dr2",
    "dr3",
    "dr6",
    "dr7",
]
X64_REGS = [
    "rax",
    "rcx",
    "rdx",
    "rbx",
    "rsp",
    "rbp",
    "rsi",
    "rdi",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15",
    "rip",
    "eflags",
    "gs",
    "fs",
    "es",
    "ds",
    "cs",
    "ss",
    "dr0",
    "dr1",
    "dr2",
    "dr3",
    "dr6",
    "dr7",
]

# disable this to show all registers
REG_FILTER_ENABLED = True

# regs not on this list are filtered out of reglist
REG_FILTER = [
    "eax",
    "ecx",
    "edx",
    "ebx",
    "esp",
    "ebp",
    "esi",
    "edi",
    "eip",
    "rax",
    "rcx",
    "rdx",
    "rbx",
    "rsp",
    "rbp",
    "rsi",
    "rdi",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15",
    "rip",
    "eflags",
    # "gs","fs","es","ds","cs","ss",
    "dr0",
    "dr1",
    "dr2",
    "dr3",
    "dr6",
    "dr7",
]
