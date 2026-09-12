"""EnderBridge 桌面启动器主窗口 - 完整复刻 Web 控制台全部功能"""
from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from . import APP_NAME
from .envcheck import EnvCheckWorker
from .server import ROOT, ServerProcess
from .theme import QSS, TEXT_DIM
from .version_compat import detect_local_version
from .webui_client import DEFAULT_BASE, WebUIClient

from .pages.audit import AuditPage
from .pages.config import ConfigPage
from .pages.console import ConsolePage
from .pages.dashboard import DashboardPage
from .pages.log import LogPage
from .pages.mods import ModsPage
from .pages.permissions import PermissionsPage
from .pages.update import UpdatePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1180, 760)
        self.setMinimumSize(960, 620)

        # 后端: 子进程 + HTTP 客户端
        self.server = ServerProcess(self)
        self.api = WebUIClient(DEFAULT_BASE, self)

        # 页面
        self.pages: dict[str, QWidget] = {}
        self._workers = []  # 持有后台线程引用

        self._build_ui()
        self.setStyleSheet(QSS)

        # 环境自检
        self._env = EnvCheckWorker(self)
        self._env.log.connect(self._env_log)
        self._env.done.connect(self._on_env_done)
        self._env.start()

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 侧边栏
        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(218)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)
        logo = QLabel("⛏ EnderBridge")
        logo.setObjectName("SidebarLogo")
        sub = QLabel(f"awbcdlp-xjk7878 GUI  ·  v{detect_local_version()}")
        sub.setObjectName("SidebarSub")
        sl.addWidget(logo); sl.addWidget(sub)

        self.stack = QStackedWidget()
        self.nav_group = QButtonGroup(self)

        # 仪表盘 / 实时日志 必须在导航里 (用户明确要求)
        def add_nav(key, text, page):
            btn = QPushButton(text)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _=False, k=key: self._goto(k))
            self.nav_group.addButton(btn)
            sl.addWidget(btn)
            self.pages[key] = page
            self.stack.addWidget(page)
            setattr(self, f"nav_{key}", btn)

        dash = DashboardPage(self.api, self.server)
        logp = LogPage(self.server)
        conp = ConsolePage(self.api)
        cfgp = ConfigPage(self.api)
        perm = PermissionsPage(self.api)
        mods = ModsPage(self.api)
        aud = AuditPage(self.api)
        upd = UpdatePage(self.api)

        add_nav("dash",   "📊  仪表盘",     dash)
        add_nav("log",    "📜  实时日志",   logp)
        add_nav("console","🖥  终端控制台", conp)
        add_nav("config", "⚙️  功能设置",   cfgp)
        add_nav("perm",   "👥  权限管理",   perm)
        add_nav("mods",   "🧩  Mod 管理",   mods)
        add_nav("audit",  "📋  审计日志",   aud)
        add_nav("upd",    "🔄  自动更新",   upd)

        sl.addStretch(1)
        foot = QLabel("127.0.0.1:18888")
        foot.setObjectName("SidebarSub")
        sl.addWidget(foot)
        root.addWidget(side)
        root.addWidget(self.stack, 1)

        self.nav_dash.setChecked(True)

        # 底部状态栏
        sb = self.statusBar()
        sb.setStyleSheet("QStatusBar{background:#1b1c22;color:#8e8e9e;} QStatusBar::item{border:none;}")
        sb.showMessage("就绪")
        self._status_bar = sb

    def _goto(self, key: str):
        idx = list(self.pages.keys()).index(key)
        self.stack.setCurrentIndex(idx)
        # 切到对应页时自动刷新数据
        w = self.pages[key]
        if hasattr(w, "load"):
            try:
                w.load()
            except Exception:
                pass

    # ---------- 环境自检 ----------
    def _env_log(self, line: str):
        if "log" in self.pages:
            self.pages["log"].append_line(line)

    def _on_env_done(self, ok: bool, msg: str):
        if not ok:
            QMessageBox.critical(self, "环境未就绪", msg or "依赖不完整, 请查看日志。")
            return
        # 环境 OK 后自动启动服务器, 等待 WebUI 就绪再刷新仪表盘
        QTimer.singleShot(300, self._boot_server)

    def _boot_server(self):
        self.append_status("正在启动服务器 ...")
        self.server.start()
        # 轮询 /api/status 直到就绪 (最多 15 秒)
        self.api.wait_ready(self._on_webui_ready, timeout_ms=20000)

    def _on_webui_ready(self, ok: bool):
        if ok:
            self.append_status("已连接 WebUI · http://127.0.0.1:18888")
            self.pages["dash"].refresh()
        else:
            self.append_status("WebUI 未就绪, 仪表盘将每 2 秒自动重试")

    def append_status(self, text: str):
        if hasattr(self, "_status_bar"):
            self._status_bar.showMessage(text, 5000)

    # ---------- 关闭 ----------
    def closeEvent(self, e):
        if self.server.is_running:
            self.server.stop()
        for w in getattr(self, "_workers", []):
            if w.isRunning():
                w.wait(2000)
        e.accept()
