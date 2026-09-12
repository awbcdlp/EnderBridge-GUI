"""本地版本检测 (独立小工具, 不依赖项目内部包结构)"""
from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def detect_local_version() -> str:
    """优先 VERSION 文件, 其次 main.py 中的 VERSION 变量"""
    vf = os.path.join(ROOT, "VERSION")
    if os.path.exists(vf):
        try:
            with open(vf, "r", encoding="utf-8") as f:
                v = f.read().strip()
            if v:
                return v
        except Exception:
            pass
    mp = os.path.join(ROOT, "main.py")
    if os.path.exists(mp):
        try:
            with open(mp, "r", encoding="utf-8") as f:
                content = f.read()
            m = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1)
        except Exception:
            pass
    return "未知"
