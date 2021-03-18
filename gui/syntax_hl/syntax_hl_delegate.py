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
    def __init__(self, parent=None):
        super(SyntaxHighlightDelegate, self).__init__(parent)

        self.doc = QTextDocument(self)

        self.disasm_columns = []
        self.value_columns = []

        self.highlighted_regs = {}
        self.reg_hl_color = prefs.REG_HL_COLOR
        self.reg_hl_bg_colors = prefs.REG_HL_BG_COLORS

        self.ignored_chars = (" ", ",", "+", "[", "]")

        self.disasm_rules = self.load_rules_file(prefs.DISASM_RULES_FILE)
        self.value_rules = self.load_rules_file(prefs.VALUE_RULES_FILE)

    def load_rules_file(self, filename: str) -> list:
        """Loads syntax highlighting rules from json file"""
        with open(filename) as f:
            return json.load(f)

    def reset(self):
        """Resets highlighter"""
        self.highlighted_regs = {}

    def paint(self, painter, option, index):
        painter.save()

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        self.doc.setPlainText(options.text)

        column = index.column()
        if column in self.disasm_columns:
            options.font.setWeight(QFont.Bold)
            self.highlight(self.doc, self.disasm_rules)
        elif column in self.value_columns:
            options.font.setWeight(QFont.Bold)
            self.highlight(self.doc, self.value_rules)

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

    def set_reg_highlight(self, reg: str, enabled: bool):
        """Enables or disables register highlight"""
        regs_hl = prefs.HL_REGS_X86
        words = regs_hl.get(reg, [reg])

        if enabled:
            self.highlighted_regs[reg] = words
        elif reg in self.highlighted_regs:
            del self.highlighted_regs[reg]

    def highlight(self, document: QTextDocument, rules: list):
        """Highlights document"""
        char_format = QTextCharFormat()
        cursor = QTextCursor(document)

        while not cursor.isNull() and not cursor.atEnd():
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)

            text = cursor.selectedText()
            color, bgcolor = self.get_register_hl_color(text, self.highlighted_regs)

            if not color:
                color, bgcolor = self.get_color(text, rules)

            if color:
                char_format.setForeground(QColor(color))

            if bgcolor:
                char_format.setBackground(QColor(bgcolor))

            if color or bgcolor:
                cursor.mergeCharFormat(char_format)
                char_format.clearBackground()

            self.move_to_next_word(document, cursor)

    def move_to_next_word(self, doc: QTextDocument, cursor: QTextCursor):
        """Moves cursor to next word"""
        while not cursor.isNull() and not cursor.atEnd():
            if doc.characterAt(cursor.position()) not in self.ignored_chars:
                return
            cursor.movePosition(QTextCursor.NextCharacter)

    def get_register_hl_color(self, word_to_check: str, regs_hl: dict) -> tuple:
        """Gets color and bgcolor if given word is found in regs_hl"""
        color_index = 0

        for words in regs_hl.values():
            if word_to_check in words:
                if color_index < len(self.reg_hl_bg_colors):
                    bg_color = self.reg_hl_bg_colors[color_index]
                else:
                    bg_color = self.reg_hl_bg_colors[-1]
                return (self.reg_hl_color, bg_color)
            color_index += 1

        return ("", "")

    def get_color(self, word_to_check: str, rules: dict) -> tuple:
        """Gets color and bgcolor if given word is found in rules"""
        for rule in rules:
            if "words" in rule:
                for word in rule["words"]:
                    if word == word_to_check:
                        return (rule["color"], rule.get("bgcolor", ""))
            if "startswith" in rule:
                for sw in rule["startswith"]:
                    if word_to_check.startswith(sw):
                        return (rule["color"], rule.get("bgcolor", ""))
            if "has" in rule:
                for has in rule["has"]:
                    if has in word_to_check:
                        return (rule["color"], rule.get("bgcolor", ""))

        return ("", "")
