"""Mod 管理页 - 客户端/服务端 Mod 列表 + 重载"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QAbstractItemView,
)

from ..theme import GREEN, RED, TEXT_DIM
from ..webui_client import WebUIClient


class ModsPage(QWidget):
    def __init__(self, api: WebUIClient, parent=None):
        super().__init__(parent)
        self.api = api

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        t = QLabel("Mod 管理"); t.setObjectName("PageTitle")
        s = QLabel("查看已加载的客户端/服务端 Mod 及可导入状态"); s.setObjectName("PageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["类型", "名称", "模块路径", "可导入"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.tbl, 1)

        row = QHBoxLayout()
        self.btn_load = QPushButton("刷新"); self.btn_load.setObjectName("GhostButton")
        self.btn_load.clicked.connect(self.load)
        self.btn_reload = QPushButton("⟳ 重载全部服务端 Mod"); self.btn_reload.setObjectName("PrimaryButton")
        self.btn_reload.clicked.connect(self._reload)
        self.lbl = QLabel(""); self.lbl.setStyleSheet(f"color:{TEXT_DIM};")
        row.addWidget(self.btn_load); row.addWidget(self.btn_reload); row.addWidget(self.lbl, 1)
        lay.addLayout(row)

    def load(self):
        self.api.get_mods(self._on_loaded)

    def _on_loaded(self, ok, data, err):
        if not ok:
            QMessageBox.warning(self, "加载失败", err); return
        mods = data.get("mods", {})
        rows = []
        for side in ("client", "server"):
            for name, info in (mods.get(side) or {}).items():
                rows.append((side, name, info.get("path", ""), bool(info.get("importable", False))))
        self.tbl.setRowCount(len(rows))
        for i, (side, name, path, ok_flag) in enumerate(rows):
            self.tbl.setItem(i, 0, QTableWidgetItem(side))
            self.tbl.setItem(i, 1, QTableWidgetItem(name))
            self.tbl.setItem(i, 2, QTableWidgetItem(str(path)))
            item = QTableWidgetItem("✓ 可导入" if ok_flag else "✗ 失败")
            item.setForeground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor(GREEN if ok_flag else RED))
            self.tbl.setItem(i, 3, item)
        self.lbl.setText(f"共 {len(rows)} 个 Mod")

    def _reload(self):
        self.api.reload_all_mods(self._on_reloaded)

    def _on_reloaded(self, ok, data, err):
        if ok:
            QMessageBox.information(self, "完成", "服务端 Mod 已重载")
            self.load()
        else:
            QMessageBox.warning(self, "重载失败", err)
