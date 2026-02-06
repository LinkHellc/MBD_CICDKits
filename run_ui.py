#!/usr/bin/env python3
"""MBD_CICDKits UI 启动入口

支持主题选择：
- 默认深色主题（工业精密风格）
- 可通过命令行参数切换到浅色主题

使用方法：
    python run_ui.py          # 默认深色主题
    python run_ui.py --light  # 浅色主题
    python run_ui.py --dark   # 深色主题
"""

import sys
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """启动应用"""
    app = QApplication(sys.argv)

    # 解析命令行参数
    theme = "dark"  # 默认主题
    if "--light" in sys.argv:
        theme = "light"
    elif "--dark" in sys.argv:
        theme = "dark"

    # 创建主窗口并应用主题
    window = MainWindow(theme=theme)
    window.show()

    print(f"MBD_CICDKits 启动 (主题: {theme})")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
