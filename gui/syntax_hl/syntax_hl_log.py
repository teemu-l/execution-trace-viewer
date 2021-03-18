"""
This syntax highlighter is modified from the following code:
    https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting

License: https://directory.fsf.org/wiki/License:BSD-3-Clause
"""

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, bgcolor="", style=""):
    """Return a QTextCharFormat with the given attributes."""
    _color = QColor()
    _color.setNamedColor(color)
    _format = QTextCharFormat()
    _format.setForeground(_color)

    if bgcolor:
        _format.setBackground(QColor(bgcolor))

    if "bold" in style:
        _format.setFontWeight(QFont.Bold)
    if "italic" in style:
        _format.setFontItalic(True)
    return _format


# Syntax styles
STYLES = {
    "instr_general": format("#8e3ca5"),
    "instr_cmp": format("green"),
    "instr_call": format("#000000", bgcolor="#00ffff"),
    "instr_branch": format("black", bgcolor="yellow"),
    "instr_cond_branch": format("red", bgcolor="yellow", style="italic"),
    "instr_arith": format("darkCyan"),
    "instr_vm": format("red", style="bold"),
    "keywords_vm": format("darkMagenta"),
    "instr_stack": format("#ff3fa8"),
    "instr_bitwise": format("red"),
    "operator": format("red"),
    "brace": format("darkMagenta"),
    "comment": format("darkGreen", style="italic"),
    "numbers": format("brown"),
}


class AsmHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the x86 ASM language."""

    instr_general = ["mov", "movzx", "movsx", "movsx", "lea"]
    instr_cmp = ["cmp", "test"]
    instr_call = ["call", "ret"]
    instr_branch = ["jmp"]
    instr_cond_branch = [
        "jne",
        "jnz",
        "je",
        "jz",
        "jg",
        "jnle",
        "jle",
        "jng",
        "jge",
        "jnl",
        "jl",
        "jnge",
        "ja",
        "jnbe",
        "jbe",
        "jna",
        "jnb",
        "jae",
        "jnc",
        "jb",
        "jnae",
        "jc",
        "jns",
        "js",
    ]
    instr_arith = ["add", "sub", "dec", "inc", "mul"]
    instr_vm = ["nor", "load", "exit", "enter", "init"]
    instr_stack = ["push", "pushad", "pushfd", "pushal", "pop", "popfd"]
    instr_bitwise = [
        "xor",
        "and",
        "or",
        "shl",
        "shr",
        "bswap",
        "rol",
        "ror",
        "neg",
        "not",
        "btc",
        "bts",
    ]

    # Operators
    operators = [
        "=",
        # Comparison
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        # Arithmetic
        "\+",
        "-",
        "\*",
        "/",
        "//",
        "\%",
        "\*\*",
        # In-place
        "\+=",
        "-=",
        "\*=",
        "/=",
        "\%=",
        # Bitwise
        "\^",
        "\|",
        "\&",
        "\~",
        ">>",
        "<<",
    ]

    # Braces
    braces = ["\[", "\]"]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        # Keyword, operator, and brace rules
        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_general"])
            for w in AsmHighlighter.instr_general
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_cmp"]) for w in AsmHighlighter.instr_cmp
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_call"]) for w in AsmHighlighter.instr_call
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_branch"])
            for w in AsmHighlighter.instr_branch
        ]
        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_cond_branch"])
            for w in AsmHighlighter.instr_cond_branch
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_arith"])
            for w in AsmHighlighter.instr_arith
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_vm"]) for w in AsmHighlighter.instr_vm
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_stack"])
            for w in AsmHighlighter.instr_stack
        ]

        rules += [
            (r"\b%s\b" % w, 0, STYLES["instr_bitwise"])
            for w in AsmHighlighter.instr_bitwise
        ]

        rules += [(r"%s" % o, 0, STYLES["operator"]) for o in AsmHighlighter.operators]

        rules += [(r"%s" % b, 0, STYLES["brace"]) for b in AsmHighlighter.braces]

        # All other rules
        rules += [
            # Numeric literals
            (r"\b[+-]?[0-9]+[lL]?\b", 0, STYLES["numbers"]),
            (r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b", 0, STYLES["numbers"]),
            (r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b", 0, STYLES["numbers"]),
            # From 'vm_' until a space or a comma
            (r"vm_[^ ,]*", 0, STYLES["keywords_vm"]),
            # From 'j' until a space or a comma
            # (r"j[^ ,]*", 0, STYLES["instr_cond_branch"]),
            # From '#' until a newline
            (r"#[^\n]*", 0, STYLES["comment"]),
            # From ';' until a newline
            (r";[^\n]*", 0, STYLES["comment"]),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
