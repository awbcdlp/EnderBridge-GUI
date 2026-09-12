# EnderBridge Desktop (PySide6 桌面版)

在原 [EnderBridge](https://github.com/Hydrooxzgen/EnderBridge) 之上包装的 **Windows / Linux / macOS 桌面 GUI 启动器**。
原项目的所有功能（WebSocket 桥接、Mod 加载、Web 控制台、AI/QQ/音乐/Ezmatic 等模组）完全保留，本壳只负责：**启停服务器、实时日志、自动更新、环境自愈**。

## ✨ 桌面版特性

- ⚡ **启动极快**：主窗口立即弹出，环境自检与更新检测在后台线程进行，不卡 UI
- 🎨 **现代化深色 UI**：PySide6 + 自定义 QSS，末影紫青配色，侧边导航 + 卡片仪表盘
- 🚦 **一键启停 / 重启** 服务器，实时显示运行状态、WS 地址、Web 控制台地址、运行时间
- 📜 **实时日志控制台**：子进程 stdout/stderr 实时着色（错误红 / 成功绿 / 警告黄），可自动滚动、可清空
- 🌐 **一键打开 Web 控制台**（`http://127.0.0.1:18888`）与工作目录
- 🔄 **自动更新**：
  - 启动后静默查询 GitHub Release
  - 有新版弹窗提示，可一键更新
  - 自动下载 → 解压 → 替换文件（保留 `config.py` / `config.json` / `permission.json` / `logs/` / `resources/`）
  - 失败时弹窗说明原因，并给出手动下载链接
- 🩹 **依赖自愈**：启动前检测 Python 3.12+ 与全部依赖（websockets / Pillow / mido / openai / websocket-client / PySide6），缺失自动 `pip install`，失败给出明确提示
- 🧊 **不侵入原项目**：原 `main.py` 一行未改，桌面壳位于 `launcher/` 目录，升级原项目即可叠加

## 📦 目录结构

```
EnderBridge-GUI/
├── launcher.py            ← 桌面 GUI 入口 (双击启动-GUI.bat)
├── launcher/              ← 桌面壳源码
│   ├── main_window.py     主窗口
│   ├── theme.py           QSS 深色主题
│   ├── envcheck.py        环境自检 + 依赖自愈
│   ├── updater.py         GitHub 检查 / 下载 / 替换
│   ├── server.py          QProcess 管理 main.py
│   └── version_compat.py  本地版本检测
├── requirements-gui.txt   桌面壳额外依赖 (PySide6)
├── 启动-GUI.bat            Windows 一键启动
├── 启动-GUI.sh             Linux / macOS 一键启动
└── (原 EnderBridge 全部文件: main.py / lib / mod / webui ...)
```

## 🚀 使用

### Windows
双击 **`启动-GUI.bat`**。
首次启动会自动安装 PySide6 与其他依赖（需要联网，约 1–3 分钟）。

### Linux / macOS
```bash
chmod +x 启动-GUI.sh
./启动-GUI.sh
# 或直接:
python3 launcher.py
```

### 首次配置
启动 GUI 后：
1. 点 **▶ 启动服务器**
2. 点 **🌐 功能设置** 进入向导
3. 在向导中完成服务器名 / WS 端口 / AI Key / QQ 等配置，保存后服务器自动重载
4. 游戏客户端连接到 GUI 仪表盘上显示的 **WS 地址**（默认 `127.0.0.1:8800`）

## 🔄 更新策略

- 桌面壳启动后会调用 `https://api.github.com/repos/Hydrooxzgen/EnderBridge/releases/latest`
- 版本号取自 `main.py` 中的 `VERSION`，与远端 `tag_name` 做语义化比较
- 更新会跳过用户数据文件：`config.py`、`config.json`、`permission.json`、`logs/`、`resources/`、`structures/`、`screenshots/`
- 更新失败（网络中断 / 磁盘权限 / 校验失败）会弹窗，并附上 Release 页面链接供手动更新

## ⚠️ 注意

- 桌面壳自身用 `QProcess` 以 `--load-without-config` 启动 `main.py`，跳过命令行首次向导；浏览器向导仍可随时通过「打开 Web 控制台」进入。
- 需要 **Python 3.12+**（原项目硬要求，使用了 PEP 701 嵌套 f-string 语法）。
- GPL-3.0 协议：本项目与原 EnderBridge 保持同一协议，衍生修改请遵守 GPL。
