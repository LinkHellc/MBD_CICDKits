"""New Project Dialog for MBD_CICDKits.

This module implements the new project configuration dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).
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
)
from PyQt6.QtCore import pyqtSignal

from core.models import ProjectConfig
from core.config import save_config, config_exists, update_config
from utils.path_utils import sanitize_filename
from utils.path_detector import auto_detect_paths

logger = logging.getLogger(__name__)


class NewProjectDialog(QDialog):
    """新建项目配置对话框

    遵循 PyQt6 类模式，使用信号槽通信。

    Architecture Decision 3.1:
    - 继承 QDialog
    - 使用 pyqtSignal 进行事件通信
    - 跨线程信号使用 Qt.ConnectionType.QueuedConnection
    """

    # 定义信号：配置保存成功时发射
    config_saved = pyqtSignal(str)  # 参数：配置文件名
    config_updated = pyqtSignal(str)  # 参数：配置文件名（编辑模式）

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
        title = "编辑项目配置" if edit_mode else "新建项目配置"
        self.setWindowTitle(title)
        self.setMinimumWidth(600)

        # 初始化 UI
        self._init_ui()

    def _init_ui(self):
        """初始化 UI 组件"""
        layout = QVBoxLayout(self)

        # 项目名称输入字段（Subtask 1.1）
        name_row = QHBoxLayout()
        name_label = QLabel("项目名称:")
        name_label.setMinimumWidth(150)
        name_row.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入项目名称（用于保存配置文件）")
        # 编辑模式下项目名称只读（Subtask 1.4）
        if self._edit_mode:
            self.name_input.setReadOnly(True)
        name_row.addWidget(self.name_input)
        layout.addLayout(name_row)

        # 创建路径输入字段
        self.path_inputs: dict[str, QLineEdit] = {}
        path_fields = [
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
        ]

        for field_key, label_text in path_fields:
            # 创建行布局
            row = QHBoxLayout()

            # 标签
            label = QLabel(f"{label_text}:")
            label.setMinimumWidth(150)
            row.addWidget(label)

            # 输入框
            input_field = QLineEdit()
            row.addWidget(input_field)

            # 浏览按钮
            browse_btn = QPushButton("浏览...")
            browse_btn.clicked.connect(
                lambda checked, key=field_key, inp=input_field: self._browse_folder(
                    key, inp
                )
            )
            row.addWidget(browse_btn)

            # 自动检测按钮（仅针对 MATLAB 和 IAR 路径）
            if field_key in ("matlab_code_path", "iar_project_path"):
                detect_key = "matlab" if field_key == "matlab_code_path" else "iar"
                auto_detect_btn = QPushButton("🔍")
                auto_detect_btn.setMaximumWidth(40)
                auto_detect_btn.setToolTip(f"自动检测{label_text}")
                auto_detect_btn.clicked.connect(
                    lambda checked, key=detect_key, inp=input_field: self._auto_detect_single_path(
                        key, inp
                    )
                )
                row.addWidget(auto_detect_btn)

            layout.addLayout(row)
            self.path_inputs[field_key] = input_field

        # 添加全局自动检测按钮
        detect_all_row = QHBoxLayout()
        detect_all_row.addStretch()
        detect_all_btn = QPushButton("🔍 自动检测所有路径")
        detect_all_btn.setToolTip("自动扫描并填充 MATLAB 和 IAR 路径")
        detect_all_btn.clicked.connect(self._auto_detect_all_paths)
        detect_all_row.addWidget(detect_all_btn)
        layout.addLayout(detect_all_row)

        # 按钮栏
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _browse_folder(self, field_key: str, input_field: QLineEdit):
        """根据字段类型选择文件或目录

        Args:
            field_key: 字段键名
            input_field: 输入框控件
        """
        if field_key == "iar_project_path":
            # IAR工程是文件，不是目录
            file, _ = QFileDialog.getOpenFileName(
                self, "选择IAR工程文件", "", "IAR工程 (*.eww);;所有文件 (*.*)"
            )
            if file:
                input_field.setText(file)
        else:
            # 其他路径是目录
            folder = QFileDialog.getExistingDirectory(
                self, "选择文件夹", "", QFileDialog.Option.ShowDirsOnly
            )
            if folder:
                input_field.setText(folder)

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
        # 创建临时配置对象进行验证
        temp_config = ProjectConfig(
            simulink_path=self.path_inputs["simulink_path"].text(),
            matlab_code_path=self.path_inputs["matlab_code_path"].text(),
            a2l_path=self.path_inputs["a2l_path"].text(),
            target_path=self.path_inputs["target_path"].text(),
            iar_project_path=self.path_inputs["iar_project_path"].text(),
        )

        # 复用 ProjectConfig 的验证方法
        errors = temp_config.validate_required_fields()

        # 额外检查路径是否存在
        for field_key, input_field in self.path_inputs.items():
            path_str = input_field.text().strip()
            if path_str:
                path = Path(path_str)
                if not path.exists():
                    errors.append(f"{field_key}: {path_str} 不存在")

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
            QMessageBox.warning(self, "验证失败", "\n".join(errors))
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
                    "无效的项目名称",
                    "项目名称不能为空或仅包含非法字符。"
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
                        "更新成功",
                        f"配置已更新: {filename}"
                    )
                    logger.info(f"配置已更新: {filename}")
                    self.config_updated.emit(filename)
                    self.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "更新失败",
                        "配置更新失败，请查看日志。"
                    )
            else:
                # 新建模式：检查配置是否已存在（AC #5）
                if config_exists(filename):
                    reply = QMessageBox.question(
                        self,
                        "配置已存在",
                        f"配置文件 '{filename}' 已存在。\n是否覆盖？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return  # 用户选择不覆盖

                if save_config(config, filename, overwrite=True):
                    QMessageBox.information(
                        self,
                        "保存成功",
                        f"配置已保存: {filename}"
                    )
                    logger.info(f"配置已保存: {filename}")
                    self.config_saved.emit(filename)
                    self.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "保存失败",
                        "配置保存失败，请查看日志。"
                    )

        except Exception as e:
            QMessageBox.critical(
                self,
                "更新失败" if self._edit_mode else "保存失败",
                f"配置{'更新' if self._edit_mode else '保存'}失败:\n{str(e)}"
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
            # 标注为自动检测（绿色背景和边框）
            input_field.setStyleSheet(
                "background-color: #e8f5e9; "
                "border: 2px solid #4CAF50; "
                "padding: 2px;"
            )
            input_field.setToolTip("自动检测的路径")
            logger.info(f"自动检测到 {detect_key} 路径: {detected_path}")
        else:
            QMessageBox.information(
                self,
                "未检测到安装",
                f"未能自动检测到 {'MATLAB' if detect_key == 'matlab' else 'IAR'} 安装。\n\n"
                f"请手动指定路径。"
            )

    def _auto_detect_all_paths(self):
        """检测所有路径（MATLAB 和 IAR）"""
        results = auto_detect_paths()

        detected_count = 0
        if results["matlab"]:
            self.path_inputs["matlab_code_path"].setText(str(results["matlab"]))
            # 添加视觉标注
            self.path_inputs["matlab_code_path"].setStyleSheet(
                "background-color: #e8f5e9; "
                "border: 2px solid #4CAF50; "
                "padding: 2px;"
            )
            self.path_inputs["matlab_code_path"].setToolTip("自动检测的路径")
            detected_count += 1

        if results["iar"]:
            self.path_inputs["iar_project_path"].setText(str(results["iar"]))
            # 添加视觉标注
            self.path_inputs["iar_project_path"].setStyleSheet(
                "background-color: #e8f5e9; "
                "border: 2px solid #4CAF50; "
                "padding: 2px;"
            )
            self.path_inputs["iar_project_path"].setToolTip("自动检测的路径")
            detected_count += 1

        if detected_count > 0:
            QMessageBox.information(
                self,
                "检测完成",
                f"成功检测到 {detected_count} 个工具路径。\n\n"
                f"检测到的路径已用绿色边框标注。"
            )
            logger.info(f"自动检测完成，检测到 {detected_count} 个工具路径")
        else:
            QMessageBox.information(
                self,
                "未检测到安装",
                "未能自动检测到任何工具安装。\n\n"
                "请手动指定所有路径。"
            )
