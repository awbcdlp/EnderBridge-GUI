"""实时日志页 - 服务器子进程 stdout/stderr 实时输出"""
from __future__ import annotations

from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from ..theme import RED, YELLOW, GREEN, CYAN


class LogPage(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        self._auto_scroll = True

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        title = QLabel("实时日志")
        title.setObjectName("PageTitle")
        sub = QLabel("服务器进程 stdout / stderr, 实时着色")
        sub.setObjectName("PageSubtitle")
        lay.addWidget(title)
        lay.addWidget(sub)

        bar = QHBoxLayout()
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setObjectName("GhostButton")
        self.btn_clear.clicked.connect(self._clear)
        self.btn_autoscroll = QPushButton("自动滚动: 开")
        self.btn_autoscroll.setObjectName("GhostButton")
        self.btn_autoscroll.setCheckable(True)
        self.btn_autoscroll.setChecked(True)
        self.btn_autoscroll.toggled.connect(self._toggle_scroll)
        bar.addWidget(self.btn_clear)
        bar.addWidget(self.btn_autoscroll)
        bar.addStretch(1)
        lay.addLayout(bar)

        self.view = QPlainTextEdit()
        self.view.setReadOnly(True)
        lay.addWidget(self.view, 1)

        server.log.connect(self.append_line)

    def append_line(self, line: str):
        fmt = QTextCharFormat()
        low = line.lower()
        if any(k in low for k in ["错误", "error", "失败", "traceback", "exception"]):
            fmt.setForeground(QColor(RED))
        elif any(k in low for k in ["[ok]", "成功", "完成", "已启动", "已保存"]):
            fmt.setForeground(QColor(GREEN))
        elif "警告" in low or "warning" in low:
            fmt.setForeground(QColor(YELLOW))
        elif "websocket" in low or "web" in low or "启动" in low:
            fmt.setForeground(QColor(CYAN))
        else:
            fmt.setForeground(QColor("#d4d4dc"))
        cur = self.view.textCursor()
        cur.movePosition(QTextCursor.End)
        cur.insertText(line + "\n", fmt)
        if self._auto_scroll:
            self.view.moveCursor(QTextCursor.End)

    def _clear(self):
        self.view.clear()

    def _toggle_scroll(self, on: bool):
        self._auto_scroll = on
        self.btn_autoscroll.setText(f"自动滚动: {'开' if on else '关'}")
