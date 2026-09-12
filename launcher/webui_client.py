"""WebUI HTTP API 客户端 - 自动重试 + 连接等待"""
from __future__ import annotations

import json
from typing import Any, Callable, Optional

from PySide6.QtCore import QObject, QUrl, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


DEFAULT_BASE = "http://127.0.0.1:18888"
_TIMEOUT_MS = 12000


class WebUIClient(QObject):
    def __init__(self, base_url: str = DEFAULT_BASE, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.base_url = base_url.rstrip("/")
        self.nam = QNetworkAccessManager(self)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, body: Optional[dict],
                cb: Optional[Callable[[bool, dict, str], None]],
                retries: int = 1) -> None:
        self._do_request(method, path, body, cb, retries_left=retries)

    def _do_request(self, method, path, body, cb, retries_left):
        url = self._url(path)
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        req.setRawHeader(b"Accept", b"application/json")
        try:
            req.setTransferTimeout(_TIMEOUT_MS)
        except Exception:
            pass

        data = b""
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        if method == "GET":
            reply = self.nam.get(req)
        elif method == "PUT":
            reply = self.nam.put(req, data)
        elif method == "POST":
            reply = self.nam.post(req, data)
        else:
            if cb:
                cb(False, {}, f"未知方法 {method}")
            return

        def on_finished():
            timer.deleteLater()
            if reply.error() != QNetworkReply.NoError:
                msg = reply.errorString()
                if "refused" in msg.lower() or "timed out" in msg.lower() or "connection" in msg.lower():
                    msg = "无法连接 WebUI (服务器可能未就绪)"
                if retries_left > 0:
                    reply.deleteLater()
                    QTimer.singleShot(600, lambda: self._do_request(
                        method, path, body, cb, retries_left - 1))
                    return
                if cb:
                    cb(False, {}, msg)
                reply.deleteLater()
                return
            raw = bytes(reply.readAll()).decode("utf-8", errors="replace")
            reply.deleteLater()
            try:
                obj = json.loads(raw) if raw else {}
            except Exception as e:
                if cb:
                    cb(False, {}, f"响应解析失败: {e}")
                return
            if isinstance(obj, dict) and obj.get("ok") is False:
                if cb:
                    cb(False, obj, obj.get("message", "未知错误"))
                return
            if cb:
                cb(True, obj, "")

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: (not reply.isFinished() and reply.abort()))
        timer.start(_TIMEOUT_MS)
        reply.finished.connect(on_finished)

    def wait_ready(self, cb: Callable[[bool], None], timeout_ms: int = 15000) -> None:
        """轮询 /api/status 直到成功; 超时后回调(False)"""
        elapsed = [0]
        tick = 400

        def poll():
            self.status(lambda ok, d, e: _done(ok))

        def _done(ok: bool):
            if ok:
                cb(True)
                return
            elapsed[0] += tick
            if elapsed[0] >= timeout_ms:
                cb(False)
                return
            QTimer.singleShot(tick, poll)

        poll()

    # ---------- API ----------
    def status(self, cb): self._request("GET", "/api/status", None, cb)
    def release_notes(self, cb): self._request("GET", "/api/release-notes", None, cb)
    def get_config(self, cb): self._request("GET", "/api/config", None, cb)
    def save_config(self, config, cb):
        self._request("PUT", "/api/config", {"config": config}, cb, retries=2)
    def get_permissions(self, cb): self._request("GET", "/api/permissions", None, cb)
    def save_permissions(self, p, cb):
        self._request("PUT", "/api/permissions", {"permissions": p}, cb, retries=2)
    def get_mods(self, cb): self._request("GET", "/api/mods", None, cb)
    def reload_all_mods(self, cb): self._request("POST", "/api/mods/reload-all", {}, cb)
    def restart_server(self, cb): self._request("POST", "/api/restart", {}, cb)
    def send_console(self, command, cb): self._request("POST", "/api/console", {"command": command}, cb)
    def update_check(self, cb): self._request("GET", "/api/update/check", None, cb)
    def update_releases(self, page, cb):
        self._request("GET", f"/api/update/releases?page={page}", None, cb)
    def update_install(self, tag, cb):
        self._request("POST", "/api/update/install", {"github_tag": tag}, cb, retries=1)
    def audit_logs(self, sender=None, type_=None, limit=50, offset=0, cb=None):
        qs = f"?limit={limit}&offset={offset}"
        if sender: qs += f"&sender={sender}"
        if type_: qs += f"&type={type_}"
        self._request("GET", f"/api/audit-logs{qs}", None, cb)
