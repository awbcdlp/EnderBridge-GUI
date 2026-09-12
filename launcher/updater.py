"""自动更新 - GitHub Release 检测 / 下载 / 解压 / 失败提示 (后台线程)"""
from __future__ import annotations

import json
import os
import re
import shutil
import ssl
import tempfile
import urllib.request
import zipfile
from typing import Optional, Tuple

from PySide6.QtCore import QThread, Signal

from . import GITHUB_REPO
from .version_compat import detect_local_version  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 更新时需要保留的用户数据 (不被覆盖)
KEEP_FILES = {"config.py", "config.json", "permission.json", "VERSION"}
KEEP_DIRS = {"logs", "resources", "structures", "screenshots"}

UA = "EnderBridge-Desktop-Launcher"


def _http_get_json(url: str, timeout: int = 15) -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def _http_download(url: str, dest: str, progress_cb) -> None:
    """下载文件到 dest, progress_cb(percent:int)"""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        total = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        tmp = dest + ".part"
        with open(tmp, "wb") as f:
            while True:
                chunk = r.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    progress_cb(int(downloaded * 100 / total))
                else:
                    progress_cb(-1)
        os.replace(tmp, dest)


def _compare(a: str, b: str) -> int:
    """a < b -> -1; a == b -> 0; a > b -> 1"""
    def norm(v: str) -> Tuple[int, ...]:
        v = (v or "").strip().lstrip("bvV ")
        out = []
        for p in v.split("."):
            m = re.match(r"(\d+)", p)
            out.append(int(m.group(1)) if m else 0)
        while len(out) < 3:
            out.append(0)
        return tuple(out[:3])
    try:
        ta, tb = norm(a), norm(b)
        return -1 if ta < tb else (1 if ta > tb else 0)
    except Exception:
        return 0


class CheckUpdateWorker(QThread):
    """仅检查更新, 不下载"""
    log = Signal(str)
    done = Signal(object)   # dict 或 None; 出错时发 error
    error = Signal(str)

    def run(self) -> None:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            self.log.emit(f"正在查询 {GITHUB_REPO} 最新 Release ...")
            data = _http_get_json(url)
            tag = data.get("tag_name", "")
            notes = data.get("body", "") or ""
            name = data.get("name", tag)
            local = detect_local_version()
            self.log.emit(f"本地版本: {local or '未知'}, 远端最新: {tag}")

            if not tag:
                self.done.emit(None)
                return

            # 找下载地址: 优先 release asset, 否则 codeload 源码 zip
            dl_url = ""
            for asset in data.get("assets", []):
                au = (asset.get("browser_download_url") or "").lower()
                if au.endswith(".zip"):
                    dl_url = asset["browser_download_url"]
                    break
            if not dl_url:
                dl_url = f"https://codeload.github.com/{GITHUB_REPO}/zip/refs/tags/{tag}"

            newer = _compare(local, tag) < 0
            self.done.emit({
                "version": tag,
                "name": name,
                "notes": notes,
                "url": dl_url,
                "newer": newer,
                "local": local,
            })
        except Exception as e:
            self.error.emit(f"检查更新失败: {e}")


class DoUpdateWorker(QThread):
    """下载 + 解压 + 替换"""
    log = Signal(str)
    progress = Signal(int)        # 0-100; -1 表示不确定
    done = Signal(bool, str)      # success, message

    def __init__(self, download_url: str, parent=None):
        super().__init__(parent)
        self._url = download_url

    def run(self) -> None:
        tmpdir = tempfile.mkdtemp(prefix="ebupdate_")
        zip_path = os.path.join(tmpdir, "update.zip")
        try:
            self.log.emit("开始下载更新包 ...")
            self._log_progress(0)
            _http_download(self._url, zip_path, self._log_progress)
            self.log.emit("下载完成, 正在解压 ...")
            self.progress.emit(95)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmpdir)

            # 找到解压后的根目录 (zip 里通常有一层 仓库名-tag/ 目录)
            inner = self._find_inner_root(tmpdir)
            self.log.emit(f"更新包内容: {inner}")

            # 备份并替换
            self.log.emit("正在替换文件 (保留 config / permission / logs) ...")
            self._apply_update(inner, ROOT)
            self.progress.emit(100)
            self.log.emit("更新完成, 请重启桌面启动器使新版本生效。")
            self.done.emit(True, "更新完成, 重启启动器后生效。")
        except Exception as e:
            self.log.emit(f"[错误] 更新失败: {e}")
            self.done.emit(False, f"更新失败: {e}\n\n你可以手动到 GitHub Release 下载最新版本:\nhttps://github.com/{GITHUB_REPO}/releases/latest")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _log_progress(self, p: int) -> None:
        self.progress.emit(p)

    @staticmethod
    def _find_inner_root(extract_dir: str) -> str:
        entries = [e for e in os.listdir(extract_dir) if e != "update.zip"]
        if len(entries) == 1:
            cand = os.path.join(extract_dir, entries[0])
            if os.path.isdir(cand):
                return cand
        return extract_dir

    def _apply_update(self, src: str, dst: str) -> None:
        """把 src 内容复制到 dst, 跳过需要保留的文件/目录"""
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if item in KEEP_FILES:
                self.log.emit(f"  保留: {item}")
                continue
            if item in KEEP_DIRS:
                # 目录合并, 不覆盖已有用户文件
                if os.path.isdir(s):
                    self._merge_dir(s, d)
                continue
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    def _merge_dir(self, src: str, dst: str) -> None:
        os.makedirs(dst, exist_ok=True)
        for root, dirs, files in os.walk(src):
            rel = os.path.relpath(root, src)
            target = os.path.join(dst, rel) if rel != "." else dst
            os.makedirs(target, exist_ok=True)
            for fn in files:
                sp = os.path.join(root, fn)
                dp = os.path.join(target, fn)
                if not os.path.exists(dp):
                    shutil.copy2(sp, dp)
