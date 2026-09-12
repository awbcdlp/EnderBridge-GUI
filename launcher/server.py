"""服务器子进程管理 - QProcess 运行 main.py, 修复 Windows GBK 乱码 + ANSI 剥离"""
from __future__ import annotations

import os
import re
import sys

from PySide6.QtCore import QProcess, QObject, Signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PY = os.path.join(ROOT, "main.py")

# ANSI 转义序列: 颜色码 \x1b[...m, 清行 \x1b[K, 光标移动等
_ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b[()][AB012]")
# 不完整的 ANSI 起始 (跨 chunk)
_ANSI_PARTIAL = re.compile(r"\x1b(\[[0-?]*[ -/]*)?$")


def _decode_chunk(raw: bytes, leftover: bytes) -> tuple[str, bytes]:
    """容错解码: 优先 UTF-8 (子进程已强制 PYTHONUTF8), 失败回退 GBK。
    维护 leftover 处理跨 chunk 的多字节字符。
    """
    buf = leftover + raw
    if not buf:
        return "", b""

    # 1) 先试 UTF-8 整段
    try:
        return buf.decode("utf-8"), b""
    except UnicodeDecodeError:
        pass

    # 2) UTF-8 末尾可能有不完整多字节字符 (最多 4 字节):
    #    逐次丢弃末尾 0~len(buf) 字节, 找到最长可解前缀
    best_text, best_left = None, buf
    max_drop = min(4, len(buf))
    for drop in range(0, max_drop + 1):
        try:
            text = buf[:len(buf) - drop].decode("utf-8")
            best_text = text
            best_left = buf[len(buf) - drop:] if drop else b""
            break
        except UnicodeDecodeError:
            continue

    # 找到可解前缀 (哪怕是空串, 也说明字节本身是合法 UTF-8 边界) → 保留剩余作 leftover
    if best_text is not None:
        return best_text, best_left

    # 3) 开头就不是合法 UTF-8 → 整段按 GBK (Windows 控制台兜底)
    try:
        return buf.decode("gbk"), b""
    except UnicodeDecodeError:
        return buf.decode("utf-8", errors="replace"), b""


def _strip_ansi(text: str) -> str:
    """剥离 ANSI 颜色/控制序列, 并清掉孤立的 CSI 起始"""
    text = _ANSI_RE.sub("", text)
    # 去掉末尾半截转义 (留到下一段)
    m = _ANSI_PARTIAL.search(text)
    if m:
        text = text[: m.start()]
    return text


class ServerProcess(QObject):
    log = Signal(str)
    started = Signal()
    stopped = Signal(int, QProcess.ExitStatus)
    status_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proc: QProcess | None = None
        self._running = False
        self._stdout_left = b""
        self._stderr_left = b""

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        if not os.path.exists(MAIN_PY):
            self.log.emit(f"[错误] 找不到主程序: {MAIN_PY}")
            return

        self.proc = QProcess()
        self.proc.setWorkingDirectory(ROOT)

        # 关键: 强制子进程用 UTF-8 输出, 避免 Windows GBK 乱码
        env = self.proc.processEnvironment()
        if env.isEmpty():
            from PySide6.QtCore import QProcessEnvironment
            env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUTF8", "1")
        env.insert("TERM", "dumb")   # 关闭 colorlog 高级 ANSI
        self.proc.setProcessEnvironment(env)

        self.proc.readyReadStandardOutput.connect(self._on_stdout)
        self.proc.readyReadStandardError.connect(self._on_stderr)
        self.proc.started.connect(self._on_started)
        self.proc.finished.connect(self._on_finished)
        self.proc.errorOccurred.connect(self._on_error)

        self._stdout_left = b""
        self._stderr_left = b""
        self.log.emit(f"$ {sys.executable} main.py --load-without-config")
        self.proc.start(sys.executable, [MAIN_PY, "--load-without-config"])

    def stop(self) -> None:
        if not self.proc or not self._running:
            return
        self.log.emit("[系统] 正在停止服务器 ...")
        self.proc.terminate()
        if not self.proc.waitForFinished(3000):
            self.proc.kill()
            self.proc.waitForFinished(2000)

    def restart(self) -> None:
        self.stop()
        self.start()

    # ---- slots ----
    def _drain(self, channel: bytes, leftover_attr: str) -> None:
        raw = bytes(channel)
        text, new_left = _decode_chunk(raw, getattr(self, leftover_attr))
        setattr(self, leftover_attr, new_left)
        text = _strip_ansi(text)
        # 按行分发; 空行也保留 (日志可读性)
        for line in text.splitlines():
            s = line.rstrip()
            if s.strip():
                self.log.emit(s)

    def _on_stdout(self) -> None:
        assert self.proc is not None
        self._drain(bytes(self.proc.readAllStandardOutput()), "_stdout_left")

    def _on_stderr(self) -> None:
        assert self.proc is not None
        self._drain(bytes(self.proc.readAllStandardError()), "_stderr_left")

    def _on_started(self) -> None:
        self._running = True
        self.status_changed.emit(True)
        self.started.emit()

    def _on_finished(self, code: int, status: QProcess.ExitStatus) -> None:
        self._running = False
        self.status_changed.emit(False)
        self.stopped.emit(code, status)

    def _on_error(self, err: QProcess.ProcessError) -> None:
        if err == QProcess.FailedToStart:
            self.log.emit("[错误] 进程启动失败 (Python 解释器或 main.py 无法运行)")
