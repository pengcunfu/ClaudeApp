"""
JSON 语法高亮器
为 JSON 编辑器提供语法高亮功能
"""
import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class JsonHighlighter(QSyntaxHighlighter):
    """JSON 语法高亮器"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 定义高亮格式

        # 1. 键名 (双引号括起来的字符串后跟冒号) - 紫色粗体
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#881391"))
        self.key_format.setFontWeight(QFont.Weight.Bold)

        # 2. 字符串值 - 绿色
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22863a"))

        # 3. 数字 - 蓝色
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#005cc5"))

        # 4. 布尔值和 null - 红色粗体
        self.literal_format = QTextCharFormat()
        self.literal_format.setForeground(QColor("#d73a49"))
        self.literal_format.setFontWeight(QFont.Weight.Bold)

        # 5. 普通字符串 - 深蓝色
        self.string_general_format = QTextCharFormat()
        self.string_general_format.setForeground(QColor("#032f62"))

    def highlightBlock(self, text):
        """高亮文本块"""
        # 先高亮关键字和特殊值
        for match in re.finditer(r'\b(true|false|null)\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.literal_format)

        # 高亮键名 (带冒号的字符串)
        for match in re.finditer(r'"[^"]+"\s*:', text):
            self.setFormat(match.start(), match.end() - match.start(), self.key_format)

        # 高亮字符串值 (冒号后的字符串)
        for match in re.finditer(r':\s*"[^"]*"', text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)

        # 高亮数字
        for match in re.finditer(r':\s*-?\d+\.?\d*([eE][+-]?\d+)?', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)

        # 高亮剩余的普通字符串(没有冒号的)
        # 这里需要更精细的处理,避免重复高亮
        for match in re.finditer(r'"[^"]*"', text):
            # 检查是否已经被高亮
            already_highlighted = False
            for i in range(match.start(), min(match.end(), len(text))):
                if self.format(i) != QTextCharFormat():
                    already_highlighted = True
                    break

            if not already_highlighted:
                self.setFormat(match.start(), match.end() - match.start(), self.string_general_format)
