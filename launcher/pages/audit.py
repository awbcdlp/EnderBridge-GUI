"""审计日志页 - GET /api/audit-logs"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QAbstractItemView,
)

from ..webui_client import WebUIClient


class AuditPage(QWidget):
    def __init__(self, api: WebUIClient, parent=None):
        super().__init__(parent)
        self.api = api

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        t = QLabel("审计日志"); t.setObjectName("PageTitle")
        s = QLabel("服务器操作审计记录"); s.setObjectName("PageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["时间", "发送者", "类型", "内容"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.tbl, 1)

        row = QHBoxLayout()
        self.btn = QPushButton("刷新"); self.btn.setObjectName("PrimaryButton")
        self.btn.clicked.connect(self.load)
        row.addWidget(self.btn); row.addStretch(1)
        lay.addLayout(row)

    def showEvent(self, e):
        super().showEvent(e)
        self.load()

    def load(self):
        self.api.audit_logs(limit=100, cb=self._on_loaded)

    def _on_loaded(self, ok, data, err):
        if not ok:
            return
        items = data.get("items") or data.get("logs") or data.get("records") or []
        # 兼容不同字段名
        if not items and isinstance(data.get("total"), int):
            items = data.get("items", [])
        self.tbl.setRowCount(len(items))
        for i, it in enumerate(items):
            self.tbl.setItem(i, 0, QTableWidgetItem(str(it.get("time") or it.get("timestamp") or it.get("ts") or "")))
            self.tbl.setItem(i, 1, QTableWidgetItem(str(it.get("sender") or it.get("player") or "")))
            self.tbl.setItem(i, 2, QTableWidgetItem(str(it.get("type") or "")))
            self.tbl.setItem(i, 3, QTableWidgetItem(str(it.get("message") or it.get("content") or "")))
