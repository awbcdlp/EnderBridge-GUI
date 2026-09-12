#!/usr/bin/env python3
"""
EnderBridge Desktop Launcher
============================
桌面 GUI 启动器入口 (PySide6)。

特性:
  - 启动极快: 主窗口先显示, 环境自检/更新检测在后台线程进行
  - 依赖自愈: 缺 PySide6 / websockets / Pillow / mido / openai 时自动 pip install
  - 自动更新: 启动后静默查询 GitHub Release, 有新版弹窗, 一键下载替换, 失败提示
  - 实时日志: 子进程 main.py 的 stdout/stderr 实时着色输出
  - 一键启停 / 打开 Web 控制台 / 打开工作目录

用法:
    python launcher.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def _ensure_pyside6() -> None:
    """缺 PySide6 时自动安装, 成功后重启进程, 失败则退出"""
    try:
        import PySide6  # noqa: F401
        return
    except ImportError:
        pass

    print("[EnderBridge Desktop] 未检测到 PySide6, 正在自动安装 ...")
    import subprocess
    cmd = [sys.executable, "-m", "pip", "install", "PySide6-Essentials>=6.6"]
    rc = subprocess.call(cmd)
    if rc != 0:
        print("[错误] PySide6 自动安装失败, 请手动执行:")
        print("       ", " ".join(cmd))
        sys.exit(1)
    # 重启本进程, 让解释器重新加载模块
    os.execv(sys.executable, [sys.executable, os.path.abspath(__file__), *sys.argv[1:]])


def main() -> int:
    _ensure_pyside6()

    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont, QPixmap, QColor, QPainter
    from PySide6.QtWidgets import QApplication, QSplashScreen

    # 高 DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("EnderBridge awbcdlp-xjk7878 GUI")
    app.setApplicationDisplayName("EnderBridge awbcdlp-xjk7878 GUI")
    app.setOrganizationName("Hydrooxzgen")

    f = QFont("Microsoft YaHei UI" if sys.platform.startswith("win") else "Segoe UI", 10)
    app.setFont(f)

    # 启动闪屏
    splash_pm = QPixmap(440, 260)
    splash_pm.fill(QColor("#141519"))
    sp = QSplashScreen(splash_pm)
    sp.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
    sp.showMessage("⛏  EnderBridge\nawbcdlp-xjk7878 GUI\n\n正在启动 ...",
                   Qt.AlignCenter | Qt.AlignVCenter, QColor("#a855f7"))
    sp.show()
    app.processEvents()

    from launcher.main_window import MainWindow
    win = MainWindow()
    win.show()
    sp.finish(win)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
