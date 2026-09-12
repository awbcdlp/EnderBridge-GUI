"""权限管理页 - owner / op / user / blocker"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from ..theme import TEXT_DIM
from ..webui_client import WebUIClient


class PermissionsPage(QWidget):
    def __init__(self, api: WebUIClient, parent=None):
        super().__init__(parent)
        self.api = api

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        t = QLabel("权限管理")
        t.setObjectName("PageTitle")
        s = QLabel("owner 为服主 (单人); op / user / blocker 每行一个游戏 ID")
        s.setObjectName("PageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        self.in_owner = QLineEdit()
        self.in_op = QPlainTextEdit(); self.in_op.setPlaceholderText("每行一个 ID")
        self.in_user = QPlainTextEdit(); self.in_user.setPlaceholderText("每行一个 ID")
        self.in_blocker = QPlainTextEdit(); self.in_blocker.setPlaceholderText("每行一个 ID")

        g = QGroupBox("权限分组")
        f = QFormLayout(g)
        f.addRow("Owner (服主)", self.in_owner)
        f.addRow("OP (管理员)", self.in_op)
        f.addRow("User (普通用户)", self.in_user)
        f.addRow("Blocker (屏蔽名单)", self.in_blocker)
        lay.addWidget(g, 1)

        row = QHBoxLayout()
        self.btn_load = QPushButton("加载"); self.btn_load.setObjectName("GhostButton")
        self.btn_load.clicked.connect(self.load)
        self.btn_save = QPushButton("保存"); self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.save)
        self.lbl = QLabel(""); self.lbl.setStyleSheet(f"color:{TEXT_DIM};")
        row.addWidget(self.btn_load); row.addWidget(self.btn_save); row.addWidget(self.lbl, 1)
        lay.addLayout(row)

    def load(self):
        self.api.get_permissions(self._on_loaded)

    def _on_loaded(self, ok, data, err):
        if not ok:
            QMessageBox.warning(self, "加载失败", err); return
        p = data.get("permissions", {})
        self.in_owner.setText(str(p.get("owner", "")))
        self.in_op.setPlainText("\n".join(p.get("op", []) or []))
        self.in_user.setPlainText("\n".join(p.get("user", []) or []))
        self.in_blocker.setPlainText("\n".join(p.get("blocker", []) or []))
        self.lbl.setText("已加载")

    def save(self):
        def names(te):
            return [x.strip() for x in te.toPlainText().splitlines() if x.strip()]
        out = {
            "owner": self.in_owner.text().strip(),
            "op": names(self.in_op),
            "user": names(self.in_user),
            "blocker": names(self.in_blocker),
        }
        self.api.save_permissions(out, self._on_saved)

    def _on_saved(self, ok, data, err):
        if ok:
            self.lbl.setText("✓ 已保存")
            QMessageBox.information(self, "成功", "权限已保存, 即时生效")
        else:
            QMessageBox.warning(self, "保存失败", err)
