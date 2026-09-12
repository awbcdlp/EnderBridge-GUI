"""终端控制台页 - 向服务器发送控制台命令 (POST /api/console)"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPlainTextEdit, QPushButton,
    QVBoxLayout, QWidget,
)

from ..theme import TEXT_DIM
from ..webui_client import WebUIClient


class ConsolePage(QWidget):
    def __init__(self, api: WebUIClient, parent=None):
        super().__init__(parent)
        self.api = api

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        t = QLabel("终端控制台"); t.setObjectName("PageTitle")
        s = QLabel("向服务器进程发送控制台命令 (与游戏内命令同源)"); s.setObjectName("PageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        self.out = QPlainTextEdit(); self.out.setReadOnly(True)
        lay.addWidget(self.out, 1)

        row = QHBoxLayout()
        self.in_cmd = QLineEdit()
        self.in_cmd.setPlaceholderText("输入命令, 回车发送, 例如: list / help / restart")
        self.in_cmd.returnPressed.connect(self._send)
        self.btn = QPushButton("发送"); self.btn.setObjectName("PrimaryButton")
        self.btn.clicked.connect(self._send)
        row.addWidget(self.in_cmd, 1); row.addWidget(self.btn)
        lay.addLayout(row)

    def _send(self):
        cmd = self.in_cmd.text().strip()
        if not cmd:
            return
        self.out.appendPlainText(f"> {cmd}")
        self.api.send_console(cmd, self._on_done)
        self.in_cmd.clear()

    def _on_done(self, ok, data, err):
        if not ok:
            self.out.appendPlainText(f"[错误] {err}")
            return
        # /api/console 返回结构取决于后端, 直接展示
        msg = data.get("message") or data.get("output") or ""
        if not msg:
            msg = str(data)
        self.out.appendPlainText(str(msg))
