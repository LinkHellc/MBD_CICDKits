"""Workflow Selection Dialog for MBD_CICDKits.

This module implements the workflow template selection dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).

Story 2.1: Select predefined workflow template
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from core.models import WorkflowConfig
from core.config import load_workflow_templates, load_custom_workflow
from ui.styles.industrial_theme import FontManager

logger = logging.getLogger(__name__)


class WorkflowSelectDialog(QDialog):
    """工作流选择对话框

    遵循 PyQt6 类模式，使用信号槽通信。

    功能：
    - 显示预定义工作流模板列表
    - 显示模板详情（描述、预计时间）
    - 支持模板选择交互
    - 选择后返回 WorkflowConfig 对象

    Architecture Decision 3.1:
    - 继承 QDialog
    - 使用 pyqtSignal 进行事件通信
    - 跨线程信号使用 Qt.ConnectionType.QueuedConnection
    """

    # 定义信号：工作流选择确认时发射
    workflow_selected = pyqtSignal(WorkflowConfig)  # 参数：选中的工作流配置

    def __init__(self, parent=None):
        """初始化对话框

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        self.setWindowTitle("⚙️ 选择工作流模板")
        self.setMinimumWidth(700)
        self.setMinimumHeight(550)

        # 应用主题样式
        self.setStyleSheet("""
            QDialog {
                background-color: #16213e;
            }
        """)

        # 加载工作流模板
        self._templates: list[WorkflowConfig] = []
        self._selected_workflow: WorkflowConfig | None = None

        # 初始化 UI
        self._init_ui()
        self._load_templates()

    def _init_ui(self):
        """初始化 UI 组件"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # ===== 标题区域 =====
        title_card = QFrame()
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("⚙️ 工作流模板")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #f1f5f9;")
        title_layout.addWidget(title)

        desc = QLabel("选择一个预定义的工作流模板来开始构建任务")
        desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
        title_layout.addWidget(desc)

        main_layout.addWidget(title_card)

        # ===== 工作流列表区域 =====
        list_container = QFrame()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(12)

        # 工作流列表
        self.workflow_list = QListWidget()
        self.workflow_list.setMinimumHeight(300)
        self.workflow_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
                color: #f1f5f9;
            }
            QListWidget::item:selected {
                background-color: #f59e0b;
                color: #16213e;
            }
            QListWidget::item:hover {
                background-color: rgba(245, 158, 11, 0.2);
            }
        """)
        self.workflow_list.itemClicked.connect(self._on_workflow_selected)
        list_layout.addWidget(self.workflow_list)

        # 详情显示区域
        self.details_label = QLabel("选择一个模板查看详情")
        self.details_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 16px;
                color: #94a3b8;
                font-size: 13px;
            }
        """)
        self.details_label.setWordWrap(True)
        self.details_label.setMinimumHeight(100)
        list_layout.addWidget(self.details_label)

        main_layout.addWidget(list_container, 1)

        # ===== 按钮区域 =====
        button_card = QFrame()
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(0, 16, 0, 0)
        button_layout.setSpacing(12)

        button_layout.addStretch()

        # Story 2.2: 添加加载自定义工作流按钮
        custom_btn = QPushButton("📁 加载自定义工作流")
        custom_btn.setMinimumHeight(44)
        custom_btn.setMinimumWidth(160)
        custom_btn.clicked.connect(self._load_custom_workflow)
        button_layout.addWidget(custom_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.confirm_btn = QPushButton("✓ 确认选择")
        self.confirm_btn.setProperty("primary", True)
        self.confirm_btn.setMinimumHeight(44)
        self.confirm_btn.setMinimumWidth(140)
        self.confirm_btn.setEnabled(False)  # 初始禁用，直到选择模板
        self.confirm_btn.clicked.connect(self._confirm_selection)
        button_layout.addWidget(self.confirm_btn)

        main_layout.addWidget(button_card)

    def _load_templates(self):
        """加载工作流模板"""
        try:
            self._templates = load_workflow_templates()
            logger.info(f"已加载 {len(self._templates)} 个工作流模板")

            # 填充列表
            for template in self._templates:
                item = QListWidgetItem()
                # 创建显示文本
                display_text = f"{template.name}\n"
                display_text += f"⏱️ 预计时间: {template.estimated_time} 分钟"
                item.setText(display_text)
                item.setData(Qt.ItemDataRole.UserRole, template)
                self.workflow_list.addItem(item)

        except Exception as e:
            logger.error(f"加载工作流模板失败: {e}")
            self.details_label.setText(f"⚠️ 加载工作流模板失败: {str(e)}")

    def _on_workflow_selected(self, item: QListWidgetItem):
        """处理工作流选择事件

        Args:
            item: 被选中的列表项
        """
        template: WorkflowConfig = item.data(Qt.ItemDataRole.UserRole)
        self._selected_workflow = template

        # 更新详情显示
        details_text = f"📋 {template.name}\n\n"
        details_text += f"描述: {template.description}\n\n"
        details_text += f"⏱️ 预计时间: {template.estimated_time} 分钟\n\n"
        details_text += "包含阶段:\n"

        for i, stage in enumerate(template.stages, 1):
            status = "✓" if stage.enabled else "○"
            details_text += f"  {status} {stage.name}"
            if stage.enabled:
                details_text += f" ({stage.timeout}秒)"
            details_text += "\n"

        self.details_label.setText(details_text)
        self.confirm_btn.setEnabled(True)

        logger.info(f"选择工作流: {template.id}")

    def _confirm_selection(self):
        """确认选择并关闭对话框"""
        if self._selected_workflow:
            self.workflow_selected.emit(self._selected_workflow)
            self.accept()
        else:
            logger.warning("未选择工作流模板")

    def _load_custom_workflow(self):
        """加载自定义工作流配置 (Story 2.2)

        打开文件选择对话框，让用户选择自定义工作流JSON文件。
        """
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择自定义工作流配置文件",
                str(Path.home()),
                "JSON 文件 (*.json);;所有文件 (*.*)"
            )

            if not file_path:
                logger.info("用户取消了自定义工作流加载")
                return

            # 加载并验证自定义工作流
            logger.info(f"正在加载自定义工作流: {file_path}")
            workflow, error_msg = load_custom_workflow(Path(file_path))

            if error_msg:
                # 显示错误消息
                QMessageBox.critical(
                    self,
                    "加载失败",
                    f"无法加载自定义工作流配置：\n\n{error_msg}",
                    QMessageBox.StandardButton.Ok
                )
                logger.error(f"加载自定义工作流失败: {error_msg}")
                return

            # 加载成功，将自定义工作流添加到列表中
            self._add_custom_workflow_to_list(workflow, Path(file_path).name)
            logger.info(f"成功加载自定义工作流: {workflow.name}")

        except Exception as e:
            logger.exception(f"加载自定义工作流时发生异常: {e}")
            QMessageBox.critical(
                self,
                "错误",
                f"加载自定义工作流时发生未知错误：\n\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def _add_custom_workflow_to_list(self, workflow: WorkflowConfig, filename: str):
        """将自定义工作流添加到列表中 (Story 2.2)

        Args:
            workflow: 加载的工作流配置对象
            filename: 源文件名
        """
        # 检查是否已存在同名工作流
        for i in range(self.workflow_list.count()):
            item = self.workflow_list.item(i)
            existing_workflow: WorkflowConfig = item.data(Qt.ItemDataRole.UserRole)
            if existing_workflow.id == workflow.id:
                # 替换现有的工作流
                self.workflow_list.takeItem(i)
                logger.info(f"替换已存在的工作流: {workflow.id}")
                break

        # 创建新的列表项
        item = QListWidgetItem()
        display_text = f"{workflow.name} (自定义)"
        display_text += f"\n⏱️ 预计时间: {workflow.estimated_time} 分钟" if workflow.estimated_time > 0 else ""
        display_text += f"\n📁 {filename}"
        item.setText(display_text)
        item.setData(Qt.ItemDataRole.UserRole, workflow)

        # 添加到列表顶部
        self.workflow_list.insertItem(0, item)

        # 自动选中
        self.workflow_list.setCurrentItem(item)
        self._on_workflow_selected(item)

    def get_selected_workflow(self) -> WorkflowConfig | None:
        """获取选中的工作流配置

        Returns:
            选中的 WorkflowConfig 对象，如果未选择则返回 None
        """
        return self._selected_workflow
