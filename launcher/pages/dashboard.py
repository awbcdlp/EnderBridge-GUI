"""仪表盘页 - 服务器状态 / 启停 / 重启 (数据来自 /api/status)"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from ..theme import ACCENT, GREEN, RED, TEXT_DIM
from ..webui_client import WebUIClient


def _card(title: str) -> tuple[QFrame, QLabel]:
    box = QFrame()
    box.setObjectName("Card")
    lay = QVBoxLayout(box)
    lay.setContentsMargins(16, 14, 16, 12)
    lay.setSpacing(4)
    t = QLabel(title)
    t.setObjectName("CardTitle")
    v = QLabel("—")
    v.setObjectName("CardValue")
    lay.addWidget(t)
    lay.addWidget(v)
    return box, v


def _fmt_uptime(seconds: float) -> str:
    s = int(seconds or 0)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


class DashboardPage(QWidget):
    def __init__(self, api: WebUIClient, server, parent=None):
        super().__init__(parent)
        self.api = api
        self.server = server  # ServerProcess

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        title = QLabel("仪表盘")
        title.setObjectName("PageTitle")
        sub = QLabel("服务器状态总览 · 数据实时来自 Web 控制台")
        sub.setObjectName("PageSubtitle")
        lay.addWidget(title)
        lay.addWidget(sub)

        # 卡片网格
        grid = QGridLayout()
        grid.setSpacing(12)
        self.card_status, self.val_status = _card("服务器状态")
        self.card_name, self.val_name = _card("服务器名称")
        self.card_port, self.val_port = _card("游戏内 WS 端口")
        self.card_webport, self.val_webport = _card("Web 控制台端口")
        self.card_clients, self.val_clients = _card("在线客户端")
        self.card_uptime, self.val_uptime = _card("运行时间")
        self.card_version, self.val_version = _card("版本")
        self.val_status.setText("未连接")
        self.val_name.setText("—")
        self.val_port.setText("—")
        self.val_webport.setText("—")
        self.val_clients.setText("0")
        self.val_uptime.setText("00:00:00")
        self.val_version.setText("—")

        positions = [(0, 0), (0, 1), (0, 2), (0, 3),
                     (1, 0), (1, 1), (1, 2), (1, 3)]
        for (r, c), card in zip(positions, [
            self.card_status, self.card_name, self.card_port, self.card_webport,
            self.card_clients, self.card_uptime, self.card_version,
        ]):
            grid.addWidget(card, r, c)
        # 让最后一个占满
        grid.setColumnStretch(4, 1)
        lay.addLayout(grid)

        # 操作按钮
        row = QHBoxLayout()
        row.setSpacing(10)
        self.btn_start = QPushButton("▶  启动服务器")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.clicked.connect(self.server.start)
        self.btn_stop = QPushButton("■  停止")
        self.btn_stop.setObjectName("DangerButton")
        self.btn_stop.clicked.connect(self.server.stop)
        self.btn_restart = QPushButton("⟳  重启服务器")
        self.btn_restart.setObjectName("GhostButton")
        self.btn_restart.clicked.connect(self._api_restart)
        self.btn_pull = QPushButton("🔄  刷新状态")
        self.btn_pull.setObjectName("GhostButton")
        self.btn_pull.clicked.connect(self.refresh)
        row.addWidget(self.btn_start)
        row.addWidget(self.btn_stop)
        row.addWidget(self.btn_restart)
        row.addStretch(1)
        row.addWidget(self.btn_pull)
        lay.addLayout(row)

        self.hint = QLabel("")
        self.hint.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        self.hint.setWordWrap(True)
        lay.addWidget(self.hint)
        lay.addStretch(1)

        # 定时刷新 (每秒)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.server.status_changed.connect(self._on_proc_status)
        self._on_proc_status(self.server.is_running)

    def _on_proc_status(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_restart.setEnabled(running)
        if not running:
            self.val_status.setText("已停止")
            self.val_status.setStyleSheet(f"color:{TEXT_DIM};font-size:26px;font-weight:700;")

    def refresh(self):
        self.api.status(self._on_status)

    def _on_status(self, ok: bool, data: dict, err: str):
        if not ok:
            self.val_status.setText("未连接")
            self.val_status.setStyleSheet(f"color:{RED};font-size:26px;font-weight:700;")
            self.hint.setText("提示: 启动服务器后, Web 控制台 (18888) 就绪, 此处自动显示实时状态。")
            return
        self.val_status.setText("运行中")
        self.val_status.setStyleSheet(f"color:{GREEN};font-size:26px;font-weight:700;")
        self.val_name.setText(str(data.get("name", "—")))
        self.val_port.setText(str(data.get("port", "—")))
        self.val_webport.setText(str(data.get("webPort", "—")))
        self.val_clients.setText(str(data.get("clients", 0)))
        self.val_uptime.setText(_fmt_uptime(data.get("uptime", 0)))
        self.val_version.setText(str(data.get("version", "—")))
        self.hint.setText("")

    def _api_restart(self):
        self.api.restart_server(lambda ok, d, e: self._on_restart(ok, e))

    def _on_restart(self, ok: bool, err: str):
        if not ok:
            self.hint.setText(f"重启失败: {err}")
        else:
            self.hint.setText("服务器正在重启, 稍候状态自动刷新 ...")
