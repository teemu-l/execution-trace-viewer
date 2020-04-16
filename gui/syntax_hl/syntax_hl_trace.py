from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QApplication,
    QStyle,
)
from PyQt5.QtGui import (
    QColor,
    QTextDocument,
    QTextCursor,
    QTextCharFormat,
    QPalette,
    QAbstractTextDocumentLayout,
)


SYNTAX_COLORS_X86 = [
    {"startswith": ("0x", "-0x",), "color": QColor("#f16a4e")},
    {"words": ("byte", "word", "dword", "qword", "ptr",), "color": QColor("#a25500")},
    {"startswith": ("pop", "push",), "color": QColor("#ff40ff"),},
    {"startswith": ("cmp",), "words": ("test", "bt",), "color": QColor("#32c435")},
    {
        "startswith": ("mov", "stos",),
        "words": ("lea", "xchg",),
        "color": QColor("#c4536a"),
    },
    {"startswith": ("j",), "words": ("ret", "call",), "color": QColor("yellow"),},
    {
        "words": ("adc", "dec", "inc", "sub", "sbb",),
        "has": ("add", "div", "mul",),
        "color": QColor("cyan"),
    },
    {
        "has": ("xor",),
        "words": (
            "and",
            "or",
            "shl",
            "shld",
            "shr",
            "shrd",
            "sal",
            "sar",
            "rol",
            "ror",
            "rcl",
            "rcr",
            "bswap",
            "neg",
            "not",
            "btc",
            "bts",
        ),
        "color": QColor("#ff2424"),
    },
]


class SyntaxHighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, arch="x86", use_darker_text_color=False):
        super(SyntaxHighlightDelegate, self).__init__(parent)
        self.doc = QTextDocument(self)
        self.syntax_colors = SYNTAX_COLORS_X86
        self.highlighted_columns = [3]
        self.use_darker_text_color = use_darker_text_color

    def paint(self, painter, option, index):
        painter.save()
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        self.doc.setPlainText(options.text)

        if index.column() in self.highlighted_columns:
            self.highlight()

        options.text = ""
        style = (
            QApplication.style() if options.widget is None else options.widget.style()
        )
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(
                QPalette.Text,
                option.palette.color(QPalette.Active, QPalette.HighlightedText),
            )
        else:
            ctx.palette.setColor(
                QPalette.Text, option.palette.color(QPalette.Active, QPalette.Text),
            )

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)

        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)

        the_constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - the_constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def highlight(self):
        char_format = QTextCharFormat()
        cursor = QTextCursor(self.doc)
        while not cursor.isNull() and not cursor.atEnd():
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            color = self.get_color(cursor.selectedText())
            if color is not None:
                if self.use_darker_text_color:
                    color = color.darker()
                char_format.setForeground(color)
                cursor.mergeCharFormat(char_format)
            self.move_to_next_word(self.doc, cursor)

    def move_to_next_word(self, doc, cursor):
        while not cursor.isNull() and not cursor.atEnd():
            if doc.characterAt(cursor.position()) not in (" ", ",", "+", "[", "]"):
                return
            cursor.movePosition(QTextCursor.NextCharacter)

    def get_color(self, word_to_check: str):
        for syntax in self.syntax_colors:
            if "words" in syntax:
                for word in syntax["words"]:
                    if word == word_to_check:
                        return syntax["color"]
            if "startswith" in syntax:
                for sw in syntax["startswith"]:
                    if word_to_check.startswith(sw):
                        return syntax["color"]
            if "has" in syntax:
                for has in syntax["has"]:
                    if has in word_to_check:
                        return syntax["color"]
        return None

