"""现代化深色主题 (QSS) - 末影紫青配色, 精致卡片/悬停过渡/发光输入框"""

BG = "#141519"
SIDEBAR = "#1b1c22"
CARD = "#22232b"
CARD_HOVER = "#2a2b35"
BORDER = "#2f313a"
TEXT = "#ececf2"
TEXT_DIM = "#8e8e9e"
ACCENT = "#a855f7"
ACCENT_HOVER = "#b86bff"
ACCENT_PRESS = "#9333ea"
CYAN = "#22d3ee"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#eab308"

QSS = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Segoe UI Variable", "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
    font-size: 13px;
}}
QMainWindow, QDialog {{ background-color: {BG}; }}
QToolTip {{
    background-color: #0c0c10; color: {TEXT};
    border: 1px solid {ACCENT}; border-radius: 6px; padding: 5px 10px;
}}

/* ===== 侧边栏 ===== */
#Sidebar {{
    background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1d1e26, stop:1 #171820);
    border-right: 1px solid {BORDER};
}}
#SidebarLogo {{
    color: {ACCENT}; font-size: 19px; font-weight: 800;
    padding: 24px 22px 4px 22px;
}}
#SidebarSub {{ color: {TEXT_DIM}; font-size: 11px; padding: 0 22px 20px 22px; }}

QPushButton#NavButton {{
    text-align: left; padding: 11px 22px;
    border: none; border-radius: 0;
    background: transparent; color: {TEXT_DIM};
    font-size: 13px; border-left: 3px solid transparent;
}}
QPushButton#NavButton:hover {{
    background-color: rgba(255,255,255,0.04); color: {TEXT};
}}
QPushButton#NavButton:checked {{
    background-color: rgba(168,85,247,0.10);
    color: {ACCENT_HOVER};
    border-left: 3px solid {ACCENT};
    font-weight: 600;
}}

/* ===== 卡片 ===== */
#Card {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 6px;
}}
#Card:hover {{ border-color: {ACCENT}; }}
#CardTitle {{ color: {TEXT_DIM}; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }}
#CardValue {{ color: {TEXT}; font-size: 26px; font-weight: 800; }}

/* ===== 按钮 ===== */
QPushButton#PrimaryButton {{
    background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {ACCENT_HOVER}, stop:1 {ACCENT});
    color: white; border: none; border-radius: 9px;
    padding: 10px 22px; font-size: 13px; font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{ background-color: {ACCENT_HOVER}; }}
QPushButton#PrimaryButton:pressed {{ background-color: {ACCENT_PRESS}; }}
QPushButton#PrimaryButton:disabled {{ background-color: #3a2f52; color: #7e7396; }}

QPushButton#DangerButton {{
    background-color: transparent; color: {RED};
    border: 1px solid rgba(239,68,68,0.5); border-radius: 9px;
    padding: 10px 22px; font-size: 13px; font-weight: 600;
}}
QPushButton#DangerButton:hover {{ background-color: rgba(239,68,68,0.12); }}
QPushButton#DangerButton:disabled {{ color: #6b5560; border-color: #4a3a40; }}

QPushButton#GhostButton {{
    background-color: {CARD}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 9px;
    padding: 9px 18px; font-size: 13px;
}}
QPushButton#GhostButton:hover {{ background-color: {CARD_HOVER}; border-color: {TEXT_DIM}; }}
QPushButton#GhostButton:pressed {{ background-color: #1c1d24; }}

/* ===== 输入控件 ===== */
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
    background-color: #191a20;
    border: 1px solid {BORDER};
    border-radius: 7px; padding: 7px 10px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: white;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus,
QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background-color: #191a20; border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
}}

/* ===== 日志/控制台 ===== */
QPlainTextEdit, QTextEdit {{
    font-family: "Cascadia Code", "JetBrains Mono", "Consolas", "Courier New", monospace;
    font-size: 12px;
}}
#logView, #consoleView {{
    background-color: #0e0f13;
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

/* ===== 表格 ===== */
QTableWidget, QTableView {{
    background-color: #191a20;
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: #2a2b33;
    color: {TEXT};
    selection-background-color: rgba(168,85,247,0.25);
    selection-color: white;
}}
QTableWidget::item, QTableView::item {{ padding: 6px; }}
QHeaderView::section {{
    background-color: {CARD}; color: {TEXT_DIM};
    padding: 8px; border: none; border-bottom: 1px solid {BORDER};
    font-weight: 600;
}}

/* ===== 进度条 ===== */
QProgressBar {{
    background-color: #191a20; border: none; border-radius: 6px;
    height: 8px; text-align: center; color: {TEXT};
}}
QProgressBar::chunk {{
    background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {ACCENT}, stop:1 {CYAN});
    border-radius: 6px;
}}

/* ===== 滚动条 ===== */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
QScrollBar::handle:vertical {{ background: #36373f; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #48495a; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 4px; }}
QScrollBar::handle:horizontal {{ background: #36373f; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ===== 标题 ===== */
QLabel#PageTitle {{
    font-size: 24px; font-weight: 800;
    padding-bottom: 2px;
}}
QLabel#PageSubtitle {{ color: {TEXT_DIM}; font-size: 12px; }}

/* 主内容区背景微微提亮 */
QStackedWidget, QScrollArea > QWidget > QWidget {{
    background-color: {BG};
}}

/* ===== 分组 ===== */
QGroupBox {{
    border: 1px solid {BORDER}; border-radius: 12px;
    margin-top: 14px; padding-top: 16px;
    color: {TEXT_DIM}; font-weight: 600;
    background-color: rgba(255,255,255,0.015);
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; padding: 0 6px;
    color: {ACCENT_HOVER};
}}

QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{
    width: 17px; height: 17px; border-radius: 5px;
    border: 1px solid {BORDER}; background: #191a20;
}}
QCheckBox::indicator:checked {{
    background: {ACCENT}; border-color: {ACCENT};
}}

QScrollArea {{ border: none; background: transparent; }}
QStatusBar {{ background: {SIDEBAR}; color: {TEXT_DIM}; }}

QSplashScreen {{
    background-color: {BG}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 12px;
}}
"""
