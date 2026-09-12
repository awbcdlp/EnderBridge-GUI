@echo off
chcp 65001 >nul
REM ============================================================
REM  EnderBridge Desktop - Windows 一键启动
REM  双击本文件即可启动桌面 GUI, 缺依赖会自动安装
REM ============================================================
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python launcher.py
    goto done
)

where py >nul 2>nul
if %errorlevel%==0 (
    py launcher.py
    goto done
)

echo [错误] 未检测到 Python。
echo 请前往 https://www.python.org/downloads/ 安装 Python 3.12+ ,
echo 安装时务必勾选 "Add Python to PATH"。
pause

:done
if errorlevel 1 (
    echo.
    echo [启动器退出] 如有错误请把上方日志发给开发者。
    pause
)
