"""Main application window for MBD_CICDKits.

This module implements the main UI window following Architecture Decision 3.1 (UI Layer).
Provides project selection, configuration display, and build workflow initiation.

Updated with Industrial Precision Theme (v1.0 - 2026-02-06)
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QMessageBox, QStatusBar, QDialog, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from core.config import list_saved_projects, load_config
from utils.errors import ConfigLoadError
from core.models import ProjectConfig
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.styles.industrial_theme import apply_industrial_theme, Colors

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """MBD_CICDKits 主窗口 - 工业精密风格

    遵循 PyQt6 类模式，提供项目配置管理和构建工作流入口。

    设计理念：
    - 深空黑背景 + 工程蓝强调色
    - 网格对齐的技术图纸感
    - 三级视觉层次（主背景、次级背景、悬浮元素）

    Signals:
        project_loaded(str): 当项目配置加载成功时发射
    """

    project_loaded = pyqtSignal(str)  # 参数：项目名称

    def __init__(self, theme: str = "dark"):
        """初始化主窗口

        Args:
            theme: 主题选择，"dark" 或 "light"
        """
        super().__init__()
        self.setWindowTitle("MBD_CICDKits - CI/CD 自动化工具")
        self.setMinimumSize(900, 700)

        # 主题设置
        self._theme = theme
        apply_industrial_theme(self, theme)

        # 当前加载的配置
        self._current_config: ProjectConfig | None = None

        # 初始化 UI
        self._init_ui()
        self._init_actions()
        self._init_menu_bar()

        # 加载项目列表
        self._refresh_project_list()

        logger.info(f"主窗口初始化完成 (主题: {theme})")

    def _init_ui(self):
        """初始化 UI 组件 - 工业精密布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # ===== 标题栏 =====
        layout.addWidget(self._create_header())

        # ===== 项目选择面板 =====
        layout.addWidget(self._create_project_panel())

        # ===== 配置显示面板 =====
        layout.addWidget(self._create_config_panel())

        # ===== 状态指示面板 =====
        layout.addWidget(self._create_status_panel())

        layout.addStretch()

        # ===== 底部分隔线 =====
        layout.addWidget(self._create_separator())

        # ===== 状态栏 =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 | 等待操作")

    def _create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("MBD_CICDKits")
        title.setProperty("heading", True)
        layout.addWidget(title)

        layout.addStretch()

        # 工具按钮（设置和帮助）
        for icon_text, tooltip in [("⚙", "设置"), ("ⓘ", "帮助")]:
            btn = QPushButton(icon_text)
            btn.setProperty("icon-btn", True)
            btn.setMinimumSize(36, 36)
            btn.setMaximumSize(36, 36)
            btn.setToolTip(tooltip)
            layout.addWidget(btn)

        return header

    def _create_project_panel(self) -> QFrame:
        """创建项目选择面板"""
        panel = QFrame()
        panel.setProperty("elevated", True)

        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 子标题
        subtitle = QLabel("项目选择")
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        # 项目选择行
        select_row = QHBoxLayout()

        self.project_combo = QComboBox()
        self.project_combo.setMinimumHeight(44)
        self.project_combo.addItem("▼ 选择项目...")
        self.project_combo.currentTextChanged.connect(self._on_project_selected)
        select_row.addWidget(self.project_combo, 1)

        # 操作按钮
        for text, prop, callback in [
            ("+ 新建", None, self._new_project),
            ("编辑", None, None),  # 待实现
            ("删除", "danger", self._delete_project),
        ]:
            btn = QPushButton(text)
            if prop:
                btn.setProperty(prop, True)
            if callback:
                btn.clicked.connect(callback)
            btn.setMinimumHeight(44)
            select_row.addWidget(btn)

        layout.addLayout(select_row)

        # 构建按钮（大号主要按钮）
        self.build_btn = QPushButton("▶ 开始构建")
        self.build_btn.setProperty("primary", True)
        self.build_btn.setMinimumHeight(52)
        self.build_btn.setEnabled(False)
        self.build_btn.clicked.connect(self._start_build)
        layout.addWidget(self.build_btn)

        return panel

    def _create_config_panel(self) -> QFrame:
        """创建配置显示面板 - 优化布局"""
        panel = QFrame()
        panel.setProperty("elevated", True)

        layout = QVBoxLayout(panel)
        layout.setSpacing(20)  # 增加间距
        layout.setContentsMargins(28, 24, 28, 24)  # 增加左右边距

        # 子标题
        subtitle = QLabel("配置路径")
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        # 路径显示网格
        grid = QGridLayout()
        grid.setSpacing(16)  # 增加行间距
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0, 0)  # 标签列不拉伸
        grid.setColumnStretch(1, 1)  # 输入框列拉伸

        self.path_labels = {}
        path_fields = [
            ("simulink_path", "Simulink 工程"),
            ("matlab_code_path", "MATLAB 代码"),
            ("a2l_path", "A2L 文件"),
            ("target_path", "目标文件"),
            ("iar_project_path", "IAR 工程"),
        ]

        for i, (field_key, label_text) in enumerate(path_fields):
            # 标签
            label = QLabel(label_text)
            label.setProperty("label", True)
            label.setMinimumWidth(100)  # 固定标签宽度
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(label, i, 0)

            # 路径显示（只读输入框）
            path_input = QLineEdit()
            path_input.setReadOnly(True)
            path_input.setText("—")
            path_input.setPlaceholderText(f"加载项目后显示 {label_text} 路径...")
            path_input.setMinimumHeight(40)  # 增加高度
            # 只读输入框默认支持文本选择
            grid.addWidget(path_input, i, 1)

            self.path_labels[field_key] = path_input

        layout.addLayout(grid)
        return panel

    def _create_status_panel(self) -> QFrame:
        """创建状态指示面板"""
        panel = QFrame()
        panel.setProperty("elevated", True)

        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        # 子标题
        subtitle = QLabel("状态指示")
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        # 环境状态
        env_row = QHBoxLayout()
        env_label = QLabel("● 环境:")
        env_label.setProperty("label", True)
        env_row.addWidget(env_label)

        self.env_status = QLabel("检测中...")
        env_row.addWidget(self.env_status)
        env_row.addStretch()
        layout.addLayout(env_row)

        # 最近构建
        build_row = QHBoxLayout()
        build_label = QLabel("● 最近构建:")
        build_label.setProperty("label", True)
        build_row.addWidget(build_label)

        self.last_build_label = QLabel("—")
        build_row.addWidget(self.last_build_label)
        build_row.addStretch()
        layout.addLayout(build_row)

        return panel

    def _create_separator(self) -> QFrame:
        """创建分隔线"""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        return sep

    def _init_actions(self):
        """初始化动作"""
        # 新建项目
        self.new_action = QAction("新建项目", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._new_project)

        # 刷新项目列表
        self.refresh_action = QAction("刷新项目列表", self)
        self.refresh_action.setShortcut("F5")
        self.refresh_action.triggered.connect(self._refresh_project_list)

        # 切换主题
        self.theme_action = QAction("切换主题", self)
        self.theme_action.setShortcut("Ctrl+T")
        self.theme_action.triggered.connect(self._toggle_theme)

        # 退出
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

    def _init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(self.theme_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _toggle_theme(self):
        """切换主题"""
        new_theme = "light" if self._theme == "dark" else "dark"
        self._theme = new_theme
        apply_industrial_theme(self, new_theme)
        self.status_bar.showMessage(f"已切换到{new_theme}主题", 3000)
        logger.info(f"主题已切换: {new_theme}")

    def _refresh_project_list(self):
        """刷新项目列表下拉框"""
        self.project_combo.clear()
        self.project_combo.addItem("▼ 选择项目...", None)

        projects = list_saved_projects()
        for project_name in projects:
            self.project_combo.addItem(project_name, project_name)

        if projects:
            self.status_bar.showMessage(f"已加载 {len(projects)} 个项目")
        else:
            self.status_bar.showMessage("无已保存的项目")

    def _on_project_selected(self, project_name: str):
        """项目选择变化时的处理

        Args:
            project_name: 选中的项目名称
        """
        if project_name == "▼ 选择项目...":
            # 清空显示
            self._clear_display()
            self.status_bar.showMessage("请选择或新建项目")
        else:
            self.status_bar.showMessage(f"已选择: {project_name}，点击'加载'按钮加载配置")

    def _load_selected_project(self):
        """加载选中的项目配置"""
        current_data = self.project_combo.currentData()
        if current_data is None:
            QMessageBox.warning(
                self,
                "未选择项目",
                "请先从下拉列表中选择一个项目。"
            )
            return

        project_name = current_data
        self._load_project_to_ui(project_name)

    def _load_project_to_ui(self, project_name: str):
        """加载项目配置到 UI

        Args:
            project_name: 项目名称
        """
        # 调用 load_config 获取配置对象
        try:
            config = load_config(project_name)
        except ConfigLoadError as e:
            # 显示结构化错误消息和建议
            error_msg = str(e)
            suggestions = "\n".join(f"  - {s}" for s in e.suggestions) if e.suggestions else "  - 查看日志获取详细信息"

            QMessageBox.warning(
                self,
                "加载失败",
                f"{error_msg}\n\n"
                f"建议操作:\n{suggestions}"
            )
            self._clear_display()
            return

        # 填充所有路径输入框
        self.path_labels["simulink_path"].setText(config.simulink_path)
        self.path_labels["matlab_code_path"].setText(config.matlab_code_path)
        self.path_labels["a2l_path"].setText(config.a2l_path)
        self.path_labels["target_path"].setText(config.target_path)
        self.path_labels["iar_project_path"].setText(config.iar_project_path)

        # 启用"开始构建"按钮
        self.build_btn.setEnabled(True)

        # 保存当前配置
        self._current_config = config

        # 显示成功状态消息
        self.status_bar.showMessage(f"✅ 已加载项目: {project_name}")

        # 记录加载操作到日志
        logger.info(f"项目配置已加载: {project_name}")

        # 发射信号
        self.project_loaded.emit(project_name)

    def _clear_display(self):
        """清空所有显示字段"""
        for input_field in self.path_labels.values():
            input_field.clear()

        self.build_btn.setEnabled(False)
        self._current_config = None
        self.last_build_label.setText("—")

    def _new_project(self):
        """打开新建项目对话框"""
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 对话框已处理保存，刷新项目列表
            self._refresh_project_list()
            logger.info("新建项目成功")

    def _delete_project(self):
        """删除选中的项目"""
        current_data = self.project_combo.currentData()
        if current_data is None:
            QMessageBox.warning(self, "未选择项目", "请先选择要删除的项目。")
            return

        project_name = current_data
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除项目 '{project_name}' 吗？\n\n此操作无法撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from core.config import delete_config
            if delete_config(project_name):
                self._refresh_project_list()
                self._clear_display()
                self.status_bar.showMessage(f"已删除项目: {project_name}")
                logger.info(f"项目已删除: {project_name}")
            else:
                QMessageBox.warning(self, "删除失败", f"无法删除项目: {project_name}")

    def _start_build(self):
        """开始构建流程"""
        if self._current_config:
            self.status_bar.showMessage("🚀 构建流程启动...")
            # TODO: 实现实际的构建流程
            QMessageBox.information(
                self,
                "构建启动",
                f"开始构建项目: {self._current_config.name}\n\n"
                "构建流程将在后续 Epic 中实现。"
            )

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 MBD_CICDKits",
            "<h3>MBD_CICDKits</h3>"
            "<p>Simulink 模型 CI/CD 自动化工具</p>"
            "<p>版本: 0.1.0 (开发中)</p>"
            "<p>功能特性:</p>"
            "<ul>"
            "<li>项目配置管理</li>"
            "<li>MATLAB 代码生成</li>"
            "<li>IAR 工程编译</li>"
            "<li>A2L 文件处理</li>"
            "</ul>"
        )

    def get_current_config(self) -> ProjectConfig | None:
        """获取当前加载的项目配置

        Returns:
            当前 ProjectConfig 对象，如果未加载则返回 None
        """
        return self._current_config
