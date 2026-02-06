"""
工业精密主题 - MBD_CICDKits

设计理念：像精密仪器般的工程工具界面
- 深色工程蓝主题 + 警示橙高亮
- 网格对齐的技术图纸感
- 微妙的机械/电子暗示

版本: 1.0
创建日期: 2026-02-06
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont


class Colors:
    """工业精密配色系统 - 深色主题"""

    # 背景色
    BG_PRIMARY = "#0B1016"        # 深空黑 - 主背景
    BG_SECONDARY = "#151C25"      # 仪器灰 - 次级背景
    BG_ELEVATED = "#1E2733"       # 面板灰 - 悬浮元素

    # 强调色
    ACCENT_BLUE = "#3B8DD0"       # 工程蓝 - 主要操作
    ACCENT_ORANGE = "#FF6B35"     # 警示橙 - 重要按钮
    ACCENT_GREEN = "#00D9A5"      # 成功绿 - 状态指示

    # 文字色（优化对比度）
    TEXT_PRIMARY = "#F0F5FA"      # 高亮白 - 主要文字
    TEXT_SECONDARY = "#B0C0D8"    # 设备灰 - 次要文字
    TEXT_MUTED = "#6A7588"        # 待机灰 - 禁用文字

    # 边框色（增强对比）
    BORDER_SUBTLE = "rgba(59, 141, 208, 0.2)"
    BORDER_FOCUS = "rgba(59, 141, 208, 0.8)"

    # 状态颜色
    STATUS_SUCCESS = "#00D9A5"
    STATUS_WARNING = "#FFB347"
    STATUS_ERROR = "#FF5C5C"
    STATUS_INFO = "#3B8DD0"


class LightColors:
    """工业精密配色系统 - 浅色主题"""

    # 背景色
    BG_PRIMARY = "#F5F7FA"        # 浅灰白
    BG_SECONDARY = "#FFFFFF"      # 纯白
    BG_ELEVATED = "#E8EDF3"       # 浅灰面板

    # 强调色（浅色背景下更深）
    ACCENT_BLUE = "#2563EB"       # 深蓝
    ACCENT_ORANGE = "#EA580C"     # 深橙
    ACCENT_GREEN = "#059669"      # 深绿

    # 文字色
    TEXT_PRIMARY = "#1A202C"      # 深黑
    TEXT_SECONDARY = "#5A6B7C"    # 中灰
    TEXT_MUTED = "#A0AEC0"        # 浅灰

    # 边框色
    BORDER_SUBTLE = "rgba(37, 99, 235, 0.15)"
    BORDER_FOCUS = "rgba(37, 99, 235, 0.6)"

    # 状态颜色
    STATUS_SUCCESS = "#059669"
    STATUS_WARNING = "#F59E0B"
    STATUS_ERROR = "#DC2626"
    STATUS_INFO = "#2563EB"


# 默认使用深色主题
_CurrentColors = Colors


def set_theme(theme: str = "dark"):
    """设置主题

    Args:
        theme: "dark" 或 "light"
    """
    global _CurrentColors
    if theme == "light":
        _CurrentColors = LightColors
    else:
        _CurrentColors = Colors


def get_colors() -> Colors:
    """获取当前主题配色"""
    return _CurrentColors


# 深色主题样式表
DARK_STYLESHEET = f"""
/* ========== 全局 ========== */
QWidget {{
    background-color: {Colors.BG_PRIMARY};
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    border: none;
}}

/* ========== 主窗口 ========== */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {Colors.BG_PRIMARY},
        stop:1 {Colors.BG_SECONDARY}
    );
}}

/* ========== 面板容器 ========== */
QFrame {{
    background-color: {Colors.BG_SECONDARY};
    border-radius: 8px;
    border: 1px solid {Colors.BORDER_SUBTLE};
}}

QFrame[elevated="true"] {{
    background-color: {Colors.BG_ELEVATED};
    border: 1px solid {Colors.BORDER_SUBTLE};
}}

/* ========== 标题 ========== */
QLabel[heading="true"] {{
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -0.5px;
}}

QLabel[subheading="true"] {{
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: {Colors.TEXT_SECONDARY};
    letter-spacing: 1px;
    text-transform: uppercase;
}}

QLabel[label="true"] {{
    font-family: 'Consolas', monospace;
    font-size: 12px;
    color: {Colors.TEXT_SECONDARY};
    padding: 4px 0px;
}}

/* ========== 输入框 ========== */
QLineEdit {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 10px 12px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    selection-background-color: {Colors.ACCENT_BLUE};
}}

QLineEdit:focus {{
    border: 1px solid {Colors.ACCENT_BLUE};
    background-color: {Colors.BG_ELEVATED};
}}

QLineEdit:hover {{
    border: 1px solid {Colors.BORDER_FOCUS};
}}

/* 自动检测的输入框（绿色高亮） */
QLineEdit[auto-detected="true"] {{
    background-color: rgba(0, 217, 165, 0.08);
    border: 1px solid rgba(0, 217, 165, 0.4);
}}

QLineEdit[auto-detected="true"]:focus {{
    border: 1px solid {Colors.ACCENT_GREEN};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 10px 12px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
}}

QComboBox:hover {{
    border: 1px solid {Colors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_ELEVATED};
    border: 1px solid {Colors.BORDER_SUBTLE};
    selection-background-color: {Colors.ACCENT_BLUE};
    selection-color: {Colors.TEXT_PRIMARY};
    padding: 4px;
}}

/* ========== 按钮 ========== */
QPushButton {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 10px 20px;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {Colors.BG_SECONDARY};
    border: 1px solid {Colors.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: {Colors.BG_ELEVATED};
}}

/* 主要按钮（蓝色） */
QPushButton[primary="true"] {{
    background-color: {Colors.ACCENT_BLUE};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}

QPushButton[primary="true"]:hover {{
    background-color: #4A9CE0;
}}

QPushButton[primary="true"]:pressed {{
    background-color: #2A7CC0;
}}

/* 危险按钮（橙色） */
QPushButton[danger="true"] {{
    background-color: {Colors.ACCENT_ORANGE};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}

QPushButton[danger="true"]:hover {{
    background-color: #FF7B4A;
}}

/* 图标按钮 */
QPushButton[icon-btn="true"] {{
    background-color: transparent;
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 8px;
    min-width: 36px;
    max-width: 36px;
}}

QPushButton[icon-btn="true"]:hover {{
    background-color: {Colors.BG_ELEVATED};
    border: 1px solid {Colors.BORDER_FOCUS};
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: {Colors.BG_PRIMARY};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.BG_ELEVATED};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {Colors.TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ========== 分隔线 ========== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {Colors.BORDER_SUBTLE};
}}

/* ========== 对话框 ========== */
QDialog {{
    background-color: {Colors.BG_SECONDARY};
}}

QDialog QLabel {{
    color: {Colors.TEXT_PRIMARY};
}}

/* ========== 状态栏 ========== */
QStatusBar {{
    background-color: {Colors.BG_PRIMARY};
    color: {Colors.TEXT_SECONDARY};
    border-top: 1px solid {Colors.BORDER_SUBTLE};
}}
"""


# 浅色主题样式表
LIGHT_STYLESHEET = f"""
/* ========== 全局 ========== */
QWidget {{
    background-color: {LightColors.BG_PRIMARY};
    color: {LightColors.TEXT_PRIMARY};
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    border: none;
}}

/* ========== 主窗口 ========== */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {LightColors.BG_PRIMARY},
        stop:1 {LightColors.BG_SECONDARY}
    );
}}

/* ========== 面板容器 ========== */
QFrame {{
    background-color: {LightColors.BG_SECONDARY};
    border-radius: 8px;
    border: 1px solid {LightColors.BORDER_SUBTLE};
}}

QFrame[elevated="true"] {{
    background-color: {LightColors.BG_ELEVATED};
    border: 1px solid {LightColors.BORDER_SUBTLE};
}}

/* ========== 标题 ========== */
QLabel[heading="true"] {{
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: {LightColors.TEXT_PRIMARY};
    letter-spacing: -0.5px;
}}

QLabel[subheading="true"] {{
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: {LightColors.TEXT_SECONDARY};
    letter-spacing: 1px;
    text-transform: uppercase;
}}

QLabel[label="true"] {{
    font-family: 'Consolas', monospace;
    font-size: 12px;
    color: {LightColors.TEXT_SECONDARY};
    padding: 4px 0px;
}}

/* ========== 输入框 ========== */
QLineEdit {{
    background-color: {LightColors.BG_SECONDARY};
    color: {LightColors.TEXT_PRIMARY};
    border: 1px solid {LightColors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 10px 12px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    selection-background-color: {LightColors.ACCENT_BLUE};
}}

QLineEdit:focus {{
    border: 1px solid {LightColors.ACCENT_BLUE};
    background-color: {LightColors.BG_SECONDARY};
}}

QLineEdit:hover {{
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

/* 自动检测的输入框（绿色高亮） */
QLineEdit[auto-detected="true"] {{
    background-color: rgba(5, 150, 105, 0.08);
    border: 1px solid rgba(5, 150, 105, 0.4);
}}

QLineEdit[auto-detected="true"]:focus {{
    border: 1px solid {LightColors.ACCENT_GREEN};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: {LightColors.BG_SECONDARY};
    color: {LightColors.TEXT_PRIMARY};
    border: 1px solid {LightColors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 10px 12px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
}}

QComboBox:hover {{
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {LightColors.BG_SECONDARY};
    border: 1px solid {LightColors.BORDER_SUBTLE};
    selection-background-color: {LightColors.ACCENT_BLUE};
    selection-color: #FFFFFF;
    padding: 4px;
}}

/* ========== 按钮 ========== */
QPushButton {{
    background-color: {LightColors.BG_ELEVATED};
    color: {LightColors.TEXT_PRIMARY};
    border: 1px solid {LightColors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 10px 20px;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {LightColors.BG_SECONDARY};
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: {LightColors.BG_ELEVATED};
}}

/* 主要按钮（蓝色） */
QPushButton[primary="true"] {{
    background-color: {LightColors.ACCENT_BLUE};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}

QPushButton[primary="true"]:hover {{
    background-color: #1D4ED8;
}}

QPushButton[primary="true"]:pressed {{
    background-color: #1E40AF;
}}

/* 危险按钮（橙色） */
QPushButton[danger="true"] {{
    background-color: {LightColors.ACCENT_ORANGE};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}

QPushButton[danger="true"]:hover {{
    background-color: #C2410C;
}}

/* 图标按钮 */
QPushButton[icon-btn="true"] {{
    background-color: transparent;
    border: 1px solid {LightColors.BORDER_SUBTLE};
    border-radius: 4px;
    padding: 8px;
    min-width: 36px;
    max-width: 36px;
}}

QPushButton[icon-btn="true"]:hover {{
    background-color: {LightColors.BG_ELEVATED};
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: {LightColors.BG_PRIMARY};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {LightColors.BG_ELEVATED};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {LightColors.TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ========== 分隔线 ========== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {LightColors.BORDER_SUBTLE};
}}

/* ========== 对话框 ========== */
QDialog {{
    background-color: {LightColors.BG_SECONDARY};
}}

QDialog QLabel {{
    color: {LightColors.TEXT_PRIMARY};
}}

/* ========== 状态栏 ========== */
QStatusBar {{
    background-color: {LightColors.BG_PRIMARY};
    color: {LightColors.TEXT_SECONDARY};
    border-top: 1px solid {LightColors.BORDER_SUBTLE};
}}
"""


def apply_industrial_theme(widget, theme: str = "dark"):
    """应用工业精密主题到指定组件

    Args:
        widget: 要应用主题的组件
        theme: "dark" 或 "light"
    """
    set_theme(theme)
    if theme == "light":
        widget.setStyleSheet(LIGHT_STYLESHEET)
    else:
        widget.setStyleSheet(DARK_STYLESHEET)