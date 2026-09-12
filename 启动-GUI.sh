#!/usr/bin/env bash
# EnderBridge Desktop - Linux / macOS 一键启动
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    exec python3 launcher.py
elif command -v python >/dev/null 2>&1; then
    exec python launcher.py
else
    echo "[错误] 未检测到 Python 3.12+"
    echo "请先安装: https://www.python.org/downloads/"
    exit 1
fi
