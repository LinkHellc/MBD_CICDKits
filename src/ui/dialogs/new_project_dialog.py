"""New Project Dialog for MBD_CICDKits.

This module implements the new project configuration dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).

Updated with Anthropic Brand Theme (v3.0 - 2026-02-07)
- Anthropic 品牌配色（橙色系）
- Poppins/Lora 字体系统
- 智能 fallback 机制
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFrame,
    QGridLayout,
    QScrollArea,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from core.models import ProjectConfig
from core.config import save_config, config_exists, update_config
from utils.path_utils import sanitize_filename
from utils.path_detector import auto_detect_paths
from ui.styles.industrial_theme import FontManager

logger = logging.getLogger(__name__)


class NewProjectDialog(QDialog):
    """新建项目配置对话框 - 现代化设计

    遵循 PyQt6 类模式，使用信号槽通信。

    设计理念：
    - 清晰的表单布局
    - 智能路径检测
    - 实时验证反馈
    - 友好的错误提示

    Architecture Decision 3.1:
    - 继承 QDialog
    - 使用 pyqtSignal 进行事件通信
    - 跨线程信号使用 Qt.ConnectionType.QueuedConnection
    """

    # 定义信号：配置保存成功时发射
    config_saved = pyqtSignal(str)  # 参数：配置文件名
    config_updated = pyqtSignal(str)  # 参数：配置文件名（编辑模式）

    # 图标映射
    FIELD_ICONS = {
        "name": "📋",
        "simulink_path": "📊",
        "matlab_code_path": "🔬",
        "a2l_path": "📝",
        "target_path": "🎯",
        "iar_project_path": "🔧",
    }

    def __init__(self, parent=None, edit_mode: bool = False):
        """初始化对话框

        Args:
            parent: 父窗口
            edit_mode: 是否为编辑模式（默认 False）
        """
        super().__init__(parent)
        self._edit_mode = edit_mode
        self._original_project_name = ""  # 编辑模式时保存原始项目名

        # 根据模式设置标题
        title = "✏️ 编辑项目配置" if edit_mode else "➕ 新建项目配置"
        self.setWindowTitle(title)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        # 应用主题样式
        self.setStyleSheet("""
            QDialog {
                background-color: #16213e;
            }
        """)

        # 初始化 UI
        self._init_ui()

    def _init_ui(self):
        """初始化 UI 组件 - 现代化表单布局"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # ===== 标题区域 =====
        title_card = QFrame()
        title_card.setProperty("elevated", True)
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("📋 项目配置")
        title.setProperty("heading", True)
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #f1f5f9;")
        title_layout.addWidget(title)

        desc = QLabel("填写以下信息以创建新的项目配置")
        desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
        title_layout.addWidget(desc)

        main_layout.addWidget(title_card)

        # ===== 表单区域（使用滚动支持小屏幕） =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # 项目名称输入字段
        form_layout.addWidget(self._create_name_field())

        # 分隔线
        sep = QLabel("─" * 80)
        sep.setStyleSheet("color: rgba(255, 255, 255, 0.1);")
        form_layout.addWidget(sep)

        # 路径配置字段
        path_fields = [
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
        ]

        self.path_inputs: dict[str, QLineEdit] = {}
        for field_key, label_text in path_fields:
            form_layout.addWidget(self._create_path_field(field_key, label_text))

        # 自动检测按钮区域
        detect_card = QFrame()
        detect_card.setProperty("elevated", True)
        detect_layout = QHBoxLayout(detect_card)
        detect_layout.setContentsMargins(20, 16, 20, 16)

        detect_layout.addStretch()

        detect_all_btn = QPushButton("🔍 智能检测所有路径")
        detect_all_btn.setProperty("success", True)
        detect_all_btn.setMinimumHeight(44)
        detect_all_btn.setToolTip("自动扫描并填充 MATLAB 和 IAR 安装路径")
        detect_all_btn.clicked.connect(self._auto_detect_all_paths)
        detect_layout.addWidget(detect_all_btn)

        detect_layout.addStretch()

        form_layout.addWidget(detect_card)
        form_layout.addStretch()

        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll, 1)

        # ===== 按钮区域 =====
        button_card = QFrame()
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(0, 16, 0, 0)
        button_layout.setSpacing(12)

        button_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 保存配置")
        save_btn.setProperty("primary", True)
        save_btn.setMinimumHeight(44)
        save_btn.setMinimumWidth(140)
        save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(save_btn)

        main_layout.addWidget(button_card)

    def _create_name_field(self) -> QFrame:
        """创建项目名称输入字段"""
        field = QFrame()
        layout = QVBoxLayout(field)
        layout.setSpacing(8)

        # 标签行
        label_row = QHBoxLayout()
        icon = QLabel(self.FIELD_ICONS["name"])
        label_row.addWidget(icon)

        label = QLabel("项目名称")
        label.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        label_row.addWidget(label)

        label_row.addStretch()

        # 编辑模式提示
        if self._edit_mode:
            hint = QLabel("(编辑模式不可更改)")
            hint.setStyleSheet("color: #f59e0b; font-size: 12px;")
            label_row.addWidget(hint)

        layout.addLayout(label_row)

        # 输入框
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：MyProject_2024")
        self.name_input.setMinimumHeight(48)
        if self._edit_mode:
            self.name_input.setReadOnly(True)
            self.name_input.setStyleSheet("""
                QLineEdit[readOnly="true"] {
                    background-color: rgba(255, 255, 255, 0.03);
                    color: #94a3b8;
                }
            """)
        layout.addWidget(self.name_input)

        # 帮助文本
        help_text = QLabel("💡 项目名称将用于标识配置文件，支持中文、英文、数字和下划线")
        help_text.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(help_text)

        return field

    def _create_path_field(self, field_key: str, label_text: str) -> QFrame:
        """创建路径输入字段

        Args:
            field_key: 字段键名
            label_text: 标签文本

        Returns:
            配置好的 QFrame
        """
        field = QFrame()
        layout = QVBoxLayout(field)
        layout.setSpacing(8)

        # 标签行
        label_row = QHBoxLayout()
        icon = QLabel(self.FIELD_ICONS.get(field_key, "📁"))
        label_row.addWidget(icon)

        label = QLabel(label_text)
        label.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        label_row.addWidget(label)

        label_row.addStretch()

        # 必填标记
        required = QLabel("* 必填")
        required.setStyleSheet("color: #ef4444; font-size: 12px;")
        label_row.addWidget(required)

        layout.addLayout(label_row)

        # 输入和按钮行
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        # 输入框
        input_field = QLineEdit()
        input_field.setPlaceholderText(f"点击浏览按钮选择{label_text}...")
        input_field.setMinimumHeight(44)
        input_row.addWidget(input_field, 1)

        # 浏览按钮
        browse_btn = QPushButton("📂 浏览")
        browse_btn.setMinimumHeight(44)
        browse_btn.setMinimumWidth(90)
        browse_btn.clicked.connect(
            lambda checked, key=field_key, inp=input_field: self._browse_folder(key, inp)
        )
        input_row.addWidget(browse_btn)

        # 自动检测按钮（仅针对 MATLAB 和 IAR 路径）
        if field_key in ("matlab_code_path", "iar_project_path"):
            detect_key = "matlab" if field_key == "matlab_code_path" else "iar"
            detect_btn = QPushButton("🔍")
            detect_btn.setMinimumHeight(44)
            detect_btn.setMinimumWidth(50)
            detect_btn.setToolTip(f"自动检测{label_text}")
            detect_btn.clicked.connect(
                lambda checked, key=detect_key, inp=input_field: self._auto_detect_single_path(
                    key, inp
                )
            )
            input_row.addWidget(detect_btn)

        layout.addLayout(input_row)

        # 保存引用
        self.path_inputs[field_key] = input_field

        return field

    def _browse_folder(self, field_key: str, input_field: QLineEdit):
        """根据字段类型选择文件或目录

        Args:
            field_key: 字段键名
            input_field: 输入框控件
        """
        if field_key == "iar_project_path":
            # IAR工程是文件，不是目录
            file, _ = QFileDialog.getOpenFileName(
                self,
                "选择 IAR 工程文件",
                "",
                "IAR 工程文件 (*.eww);;所有文件 (*.*)"
            )
            if file:
                input_field.setText(file)
                self._mark_field_validated(input_field, True)
        else:
            # 其他路径是目录
            folder = QFileDialog.getExistingDirectory(
                self,
                f"选择 {field_key.replace('_', ' ').title()} 文件夹",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            if folder:
                input_field.setText(folder)
                self._mark_field_validated(input_field, True)

    def _mark_field_validated(self, input_field: QLineEdit, valid: bool):
        """标记字段验证状态（视觉效果）

        Args:
            input_field: 输入框控件
            valid: 是否有效
        """
        if valid:
            input_field.setProperty("auto-detected", True)
        else:
            input_field.setProperty("auto-detected", False)

    def set_config(self, config: ProjectConfig):
        """加载现有配置到 UI 字段（编辑模式）

        Args:
            config: 要加载的配置对象
        """
        self._original_project_name = config.name
        self.name_input.setText(config.name)
        self.path_inputs["simulink_path"].setText(config.simulink_path)
        self.path_inputs["matlab_code_path"].setText(config.matlab_code_path)
        self.path_inputs["a2l_path"].setText(config.a2l_path)
        self.path_inputs["target_path"].setText(config.target_path)
        self.path_inputs["iar_project_path"].setText(config.iar_project_path)

    def _validate_paths(self) -> list[str]:
        """验证所有路径已填写且存在

        Returns:
            错误列表，空列表表示有效
        """
        errors = []

        # 创建临时配置对象进行验证
        try:
            temp_config = ProjectConfig(
                simulink_path=self.path_inputs["simulink_path"].text(),
                matlab_code_path=self.path_inputs["matlab_code_path"].text(),
                a2l_path=self.path_inputs["a2l_path"].text(),
                target_path=self.path_inputs["target_path"].text(),
                iar_project_path=self.path_inputs["iar_project_path"].text(),
            )

            # 复用 ProjectConfig 的验证方法
            errors = temp_config.validate_required_fields()
        except Exception as e:
            errors.append(f"配置验证失败: {str(e)}")

        # 额外检查路径是否存在
        for field_key, input_field in self.path_inputs.items():
            path_str = input_field.text().strip()
            if path_str:
                path = Path(path_str)
                if not path.exists():
                    errors.append(f"{field_key}: 路径不存在 - {path_str}")

        return errors

    def _save_config(self):
        """保存配置（增强版：包含覆盖检测和文件名清理）

        项目名称获取逻辑：
        1. 优先使用用户手动输入的项目名称
        2. 如果用户未输入，自动从 Simulink 工程路径提取目录名作为项目名称
        3. 清理文件名中的非法字符（使用 sanitize_filename）
        """
        # 验证路径
        errors = self._validate_paths()
        if errors:
            QMessageBox.warning(
                self,
                "⚠️ 验证失败",
                "以下项目需要修正：\n\n" + "\n".join(f"• {e}" for e in errors)
            )
            return

        # 获取项目名称
        if self._edit_mode:
            # 编辑模式：使用原始项目名称
            filename = self._original_project_name
        else:
            # 新建模式：获取并清理项目名称
            raw_name = self.name_input.text().strip()
            if not raw_name:
                # 如果用户没有输入项目名称，从 Simulink 路径自动提取
                simulink_path = self.path_inputs["simulink_path"].text()
                raw_name = Path(simulink_path).name

            # 清理文件名（使用 sanitize_filename）
            filename = sanitize_filename(raw_name)

            if not filename or filename == "unnamed_project":
                QMessageBox.warning(
                    self,
                    "⚠️ 无效的项目名称",
                    "项目名称不能为空或仅包含非法字符。\n\n请输入有效的项目名称。"
                )
                return

        # 创建配置对象
        config = ProjectConfig(
            name=filename,
            simulink_path=self.path_inputs["simulink_path"].text(),
            matlab_code_path=self.path_inputs["matlab_code_path"].text(),
            a2l_path=self.path_inputs["a2l_path"].text(),
            target_path=self.path_inputs["target_path"].text(),
            iar_project_path=self.path_inputs["iar_project_path"].text(),
        )

        # 保存配置
        try:
            if self._edit_mode:
                # 编辑模式：调用 update_config
                if update_config(filename, config):
                    QMessageBox.information(
                        self,
                        "✅ 更新成功",
                        f"配置已更新：{filename}"
                    )
                    logger.info(f"配置已更新: {filename}")
                    self.config_updated.emit(filename)
                    self.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "❌ 更新失败",
                        "配置更新失败，请查看日志。"
                    )
            else:
                # 新建模式：检查配置是否已存在
                if config_exists(filename):
                    reply = QMessageBox.question(
                        self,
                        "📋 配置已存在",
                        f"配置文件 '{filename}' 已存在。\n\n是否覆盖现有配置？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return  # 用户选择不覆盖

                if save_config(config, filename, overwrite=True):
                    QMessageBox.information(
                        self,
                        "✅ 保存成功",
                        f"配置已保存：{filename}\n\n您现在可以从主窗口选择此项目开始工作。"
                    )
                    logger.info(f"配置已保存: {filename}")
                    self.config_saved.emit(filename)
                    self.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "❌ 保存失败",
                        "配置保存失败，请查看日志。\n\n可能原因：\n• 磁盘空间不足\n• 权限不足"
                    )

        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ 操作失败",
                f"配置{'更新' if self._edit_mode else '保存'}失败：\n\n{str(e)}"
            )

    def _auto_detect_single_path(self, detect_key: str, input_field: QLineEdit):
        """检测单个路径

        Args:
            detect_key: 检测类型 ("matlab" 或 "iar")
            input_field: 要填充的输入框控件
        """
        from utils.path_detector import detect_matlab_installations, detect_iar_installations

        detected_path = None
        if detect_key == "matlab":
            detected_path = detect_matlab_installations()
        elif detect_key == "iar":
            detected_path = detect_iar_installations()

        if detected_path:
            input_field.setText(str(detected_path))
            self._mark_field_validated(input_field, True)
            logger.info(f"自动检测到 {detect_key} 路径: {detected_path}")
        else:
            QMessageBox.information(
                self,
                "🔍 未检测到安装",
                f"未能自动检测到 {'MATLAB' if detect_key == 'matlab' else 'IAR'} 安装。\n\n"
                f"请手动指定路径或检查软件是否已正确安装。"
            )

    def _auto_detect_all_paths(self):
        """检测所有路径（MATLAB 和 IAR）"""
        results = auto_detect_paths()

        detected_count = 0
        if results["matlab"]:
            self.path_inputs["matlab_code_path"].setText(str(results["matlab"]))
            self._mark_field_validated(self.path_inputs["matlab_code_path"], True)
            detected_count += 1

        if results["iar"]:
            self.path_inputs["iar_project_path"].setText(str(results["iar"]))
            self._mark_field_validated(self.path_inputs["iar_project_path"], True)
            detected_count += 1

        if detected_count > 0:
            QMessageBox.information(
                self,
                "✅ 检测完成",
                f"成功检测到 {detected_count} 个工具路径！\n\n"
                f"检测到的路径已用绿色边框标注。\n\n"
                f"请确认路径是否正确，然后点击保存。"
            )
            logger.info(f"自动检测完成，检测到 {detected_count} 个工具路径")
        else:
            QMessageBox.warning(
                self,
                "⚠️ 未检测到安装",
                "未能自动检测到任何工具安装。\n\n"
                "请手动指定所有路径，或确认：\n"
                "• MATLAB/IAR 已正确安装\n"
                "• 安装路径在常见位置\n"
                "• 具有读取权限"
            )
