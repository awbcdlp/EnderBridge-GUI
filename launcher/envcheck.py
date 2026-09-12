"""环境自检与依赖自愈 - 在后台线程运行,不阻塞 UI"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import List

from PySide6.QtCore import QThread, Signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 包名 -> 导入名
IMPORT_NAMES = {
    "websockets": "websockets",
    "Pillow": "PIL",
    "mido": "mido",
    "openai": "openai",
    "websocket-client": "websocket",
    "PySide6": "PySide6",
}

REQ_FILE = os.path.join(ROOT, "requirements.txt")
REQ_GUI_FILE = os.path.join(ROOT, "requirements-gui.txt")


def _read_pip_names(path: str) -> List[str]:
    names: List[str] = []
    if not os.path.exists(path):
        return names
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = line.split("==")[0].split(">=")[0].split("<")[0].split("~=")[0].strip()
            if name:
                names.append(name)
    return names


def is_installed(dep: str) -> bool:
    imp = IMPORT_NAMES.get(dep, dep)
    try:
        return importlib.util.find_spec(imp) is not None
    except (ImportError, ValueError):
        return False


def check_python_version() -> str:
    """返回空串表示 OK,否则返回错误描述"""
    if sys.version_info < (3, 12):
        return (f"当前 Python 版本 {sys.version_info.major}.{sys.version_info.minor} 过低,"
                f"EnderBridge 需要 Python 3.12 或更高版本。\n"
                f"请前往 https://www.python.org/downloads/ 安装 Python 3.12+ 后重新启动。")
    return ""


class EnvCheckWorker(QThread):
    """后台环境自检: 输出日志行; 完成后发 done(ok: bool, message: str)"""
    log = Signal(str)
    done = Signal(bool, str)

    def run(self) -> None:  # noqa: D401
        # 1. Python 版本
        ver_err = check_python_version()
        if ver_err:
            self.log.emit(f"[错误] {ver_err}")
            self.done.emit(False, ver_err)
            return
        self.log.emit(f"[OK] Python {sys.version.split()[0]}")

        # 2. 汇总依赖
        deps = _read_pip_names(REQ_FILE) + ["PySide6"]
        missing = [d for d in deps if not is_installed(d)]

        if not missing:
            self.log.emit("[OK] 所有依赖已就绪")
            self.done.emit(True, "")
            return

        self.log.emit(f"[信息] 缺少依赖: {', '.join(missing)}")
        self.log.emit("[信息] 正在自动安装 (首次可能需要几分钟, 请耐心等待)...")

        # 用一行 pip 安装全部缺失依赖
        cmd = [sys.executable, "-m", "pip", "install", *missing]
        self.log.emit("$ " + " ".join(cmd))
        try:
            proc = subprocess.Popen(
                cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    self.log.emit("  " + line)
            rc = proc.wait()
        except Exception as e:
            self.log.emit(f"[错误] 安装过程异常: {e}")
            self.done.emit(False, f"依赖安装异常: {e}")
            return

        if rc != 0:
            msg = f"pip install 失败 (退出码 {rc})。请手动执行: {sys.executable} -m pip install -r requirements.txt"
            self.log.emit(f"[错误] {msg}")
            self.done.emit(False, msg)
            return

        still = [d for d in deps if not is_installed(d)]
        if still:
            msg = f"安装后仍缺少: {', '.join(still)}"
            self.log.emit(f"[错误] {msg}")
            self.done.emit(False, msg)
            return

        self.log.emit("[OK] 依赖安装完成, 环境就绪")
        self.done.emit(True, "")
