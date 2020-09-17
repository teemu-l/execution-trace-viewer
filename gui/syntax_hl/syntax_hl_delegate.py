import json

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
    QFont,
)

from core import prefs


class SyntaxHighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, arch: str = "x86", dark_theme: bool = False):
        super(SyntaxHighlightDelegate, self).__init__(parent)
        self.doc = QTextDocument(self)
        self.highlighted_columns = [3]

        self.syntax_colors = []
        self.custom_hl = []
        self.register_hl = {}

        if dark_theme:
            self.load_syntax_file("gui/syntax_hl/syntax_x86_dark.txt")
            self.reg_hl_color = QColor("#000000")
            self.reg_hl_bg_color = QColor("#ffffff")
        else:
            self.load_syntax_file("gui/syntax_hl/syntax_x86_light.txt")
            self.reg_hl_color = QColor("#ffffff")
            self.reg_hl_bg_color = QColor("#333333")

    def set_reg_highlight(self, reg: str, enabled: bool):

        regs_hl = prefs.HL_REGS_X86
        words = regs_hl.get(reg, [reg])

        if enabled:
            self.register_hl[reg] = words
        elif reg in self.register_hl:
            del self.register_hl[reg]

    def load_syntax_file(self, filename: str):
        with open(filename) as f:
            self.syntax_colors = json.load(f)

    def paint(self, painter, option, index):
        painter.save()

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        self.doc.setPlainText(options.text)

        if index.column() in self.highlighted_columns:
            options.font.setWeight(QFont.Bold)
            self.highlight()

        self.doc.setDefaultFont(options.font)

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
                QPalette.Text,
                option.palette.color(QPalette.Active, QPalette.Text),
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

            color = self.get_register_hl_color(cursor.selectedText())
            if color is not None:
                char_format.setBackground(self.reg_hl_bg_color)
            else:
                color = self.get_color(cursor.selectedText())

            if color is not None:
                char_format.setForeground(color)
                cursor.mergeCharFormat(char_format)

            char_format.clearBackground()
            self.move_to_next_word(self.doc, cursor)

    def move_to_next_word(self, doc, cursor):
        while not cursor.isNull() and not cursor.atEnd():
            if doc.characterAt(cursor.position()) not in (" ", ",", "+", "[", "]"):
                return
            cursor.movePosition(QTextCursor.NextCharacter)

    def get_register_hl_color(self, word_to_check: str):
        for words in self.register_hl.values():
            if word_to_check in words:
                return QColor(self.reg_hl_color)
        return None

    def get_color(self, word_to_check: str):

        for syntax in self.syntax_colors:
            if "words" in syntax:
                for word in syntax["words"]:
                    if word == word_to_check:
                        return QColor(syntax["color"])
            if "startswith" in syntax:
                for sw in syntax["startswith"]:
                    if word_to_check.startswith(sw):
                        return QColor(syntax["color"])
            if "has" in syntax:
                for has in syntax["has"]:
                    if has in word_to_check:
                        return QColor(syntax["color"])

        return None
