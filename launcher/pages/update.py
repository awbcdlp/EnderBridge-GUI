"""更新页 - 复用 WebUI 后端的 /api/update/* 接口"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout,
    QWidget,
)

from ..theme import GREEN, RED, TEXT_DIM
from ..webui_client import WebUIClient


class UpdatePage(QWidget):
    def __init__(self, api: WebUIClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._latest_tag = ""

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        t = QLabel("自动更新"); t.setObjectName("PageTitle")
        s = QLabel("通过 WebUI 后端与 GitHub Release 对接"); s.setObjectName("PageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        self.lbl_cur = QLabel("当前版本: —")
        self.lbl_latest = QLabel("最新版本: 未检查")
        self.lbl_cur.setStyleSheet("font-size:14px;")
        self.lbl_latest.setStyleSheet("font-size:14px;")
        lay.addWidget(self.lbl_cur)
        lay.addWidget(self.lbl_latest)

        row = QHBoxLayout()
        self.btn_check = QPushButton("检查更新"); self.btn_check.setObjectName("PrimaryButton")
        self.btn_check.clicked.connect(self._check)
        self.btn_install = QPushButton("安装更新"); self.btn_install.setObjectName("PrimaryButton")
        self.btn_install.clicked.connect(self._install)
        self.btn_install.setEnabled(False)
        row.addWidget(self.btn_check); row.addWidget(self.btn_install); row.addStretch(1)
        lay.addLayout(row)

        self.notes = QPlainTextEdit(); self.notes.setReadOnly(True)
        lay.addWidget(self.notes, 1)

    def _check(self):
        self.notes.setPlainText("正在检查 ...")
        self.api.update_check(self._on_checked)

    def _on_checked(self, ok, data, err):
        if not ok:
            self.notes.setPlainText(f"[错误] {err}")
            QMessageBox.warning(self, "检查更新失败", err)
            return
        cur = data.get("current", "?")
        latest = data.get("latest") or "?"
        self.lbl_cur.setText(f"当前版本: {cur}")
        self.lbl_latest.setText(f"最新版本: {latest}")
        if data.get("update_available"):
            self._latest_tag = latest
            self.btn_install.setEnabled(True)
            self.notes.setPlainText(
                f"发现新版本 {latest}\n发布于 {data.get('published_at','')}\n\n"
                + (data.get("body") or "")
            )
        else:
            self.btn_install.setEnabled(False)
            self.notes.setPlainText("✓ 当前已是最新版本\n\n" + (data.get("body") or ""))

    def _install(self):
        if not self._latest_tag:
            return
        ret = QMessageBox.question(self, "确认更新", f"将更新到 {self._latest_tag}, 服务器会自动重启, 继续?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ret != QMessageBox.Yes:
            return
        self.btn_install.setEnabled(False)
        self.notes.appendPlainText("正在安装, 请稍候 ...")
        self.api.update_install(self._latest_tag, self._on_installed)

    def _on_installed(self, ok, data, err):
        if ok:
            self.notes.appendPlainText("✓ " + (data.get("message", "更新完成, 服务器重启中")))
            QMessageBox.information(self, "完成", data.get("message", "更新完成"))
        else:
            self.notes.appendPlainText(f"[错误] {err}")
            QMessageBox.critical(self, "更新失败", err)
        self.btn_install.setEnabled(bool(self._latest_tag))
