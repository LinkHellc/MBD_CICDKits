"""Configuration Error Dialog for MBD_CICDKits.

This module implements the configuration error display dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).

Story 2.2: Load custom workflow configuration - Task 5
"""

import logging
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class ConfigErrorDialog(QDialog):
    """配置错误提示对话框

    遵循 PyQt6 类模式，用于显示配置加载/验证错误。

    功能：
    - 显示错误标题和描述
    - 显示具体的错误位置
    - 显示修复建议
    - 提供关闭按钮

    Architecture Decision 3.1:
    - 继承 QDialog
    - 简洁的UI设计
    - 清晰的错误信息展示
    """

    def __init__(
        self,
        error_title: str,
        error_message: str,
        error_details: str = "",
        suggestions: list[str] = None,
        parent=None
    ):
        """初始化对话框

        Args:
            error_title: 错误标题
            error_message: 主要错误信息
            error_details: 详细的错误信息（可选）
            suggestions: 修复建议列表（可选）
            parent: 父窗口
        """
        super().__init__(parent)

        self.setWindowTitle("⚠️ 配置错误")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setModal(True)  # 模态对话框

        # 应用主题样式
        self.setStyleSheet("""
            QDialog {
                background-color: #16213e;
            }
        """)

        # 初始化 UI
        self._init_ui(error_title, error_message, error_details, suggestions)

    def _init_ui(
        self,
        error_title: str,
        error_message: str,
        error_details: str,
        suggestions: list[str]
    ):
        """初始化 UI 组件

        Args:
            error_title: 错误标题
            error_message: 主要错误信息
            error_details: 详细的错误信息
            suggestions: 修复建议列表
        """
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # ===== 错误图标和标题 =====
        header_layout = QHBoxLayout()

        # 错误图标
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(icon_label)

        # 错误标题
        title = QLabel(error_title)
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #ef4444;")
        title.setWordWrap(True)
        header_layout.addWidget(title, 1)

        main_layout.addLayout(header_layout)

        # ===== 错误信息 =====
        error_container = QFrame()
        error_container.setStyleSheet("""
            QFrame {
                background-color: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 8px;
            }
        """)
        error_layout = QVBoxLayout(error_container)
        error_layout.setContentsMargins(16, 16, 16, 16)

        error_text = QLabel(error_message)
        error_text.setStyleSheet("color: #fca5a5; font-size: 14px;")
        error_text.setWordWrap(True)
        error_layout.addWidget(error_text)

        main_layout.addWidget(error_container)

        # ===== 详细信息（如果有）=====
        if error_details:
            details_container = QFrame()
            details_container.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                }
            """)
            details_layout = QVBoxLayout(details_container)
            details_layout.setContentsMargins(16, 16, 16, 16)

            details_label = QLabel("详细信息：")
            details_label.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 13px;")
            details_layout.addWidget(details_label)

            details_scroll = QScrollArea()
            details_scroll.setWidgetResizable(True)
            details_scroll.setMaximumHeight(150)
            details_scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: rgba(255, 255, 255, 0.1);
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                }
            """)

            details_text = QLabel(error_details)
            details_text.setStyleSheet("color: #cbd5e1; font-size: 12px; font-family: monospace;")
            details_text.setWordWrap(True)
            details_scroll.setWidget(details_text)
            details_layout.addWidget(details_scroll)

            main_layout.addWidget(details_container)

        # ===== 修复建议（如果有）=====
        if suggestions:
            suggestions_container = QFrame()
            suggestions_container.setStyleSheet("""
                QFrame {
                    background-color: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 8px;
                }
            """)
            suggestions_layout = QVBoxLayout(suggestions_container)
            suggestions_layout.setContentsMargins(16, 16, 16, 16)

            suggestions_label = QLabel("💡 修复建议：")
            suggestions_label.setStyleSheet("font-weight: 600; color: #93c5fd; font-size: 13px;")
            suggestions_layout.addWidget(suggestions_label)

            for idx, suggestion in enumerate(suggestions, 1):
                suggestion_item = QLabel(f"{idx}. {suggestion}")
                suggestion_item.setStyleSheet("color: #bfdbfe; font-size: 13px; padding-left: 8px;")
                suggestion_item.setWordWrap(True)
                suggestions_layout.addWidget(suggestion_item)

            main_layout.addWidget(suggestions_container)

        # ===== 关闭按钮 =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setMinimumHeight(44)
        close_btn.setMinimumWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f1f5f9;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:pressed {
                background-color: #64748b;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)


def show_config_error(
    error_title: str,
    error_message: str,
    error_details: str = "",
    suggestions: list[str] = None,
    parent=None
) -> None:
    """显示配置错误对话框的便捷函数

    Args:
        error_title: 错误标题
        error_message: 主要错误信息
        error_details: 详细的错误信息
        suggestions: 修复建议列表
        parent: 父窗口
    """
    dialog = ConfigErrorDialog(
        error_title=error_title,
        error_message=error_message,
        error_details=error_details,
        suggestions=suggestions,
        parent=parent
    )
    dialog.exec()
