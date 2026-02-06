"""Unit tests for Story 1.3: Load saved project configuration.

Tests the list_saved_projects() function and enhanced load_config() behavior.
Code Review Fixes (2026-02-06): Updated to expect ConfigLoadError instead of None.
"""

import pytest
import tempfile
from pathlib import Path

# 确保 src 在路径中
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.models import ProjectConfig
from core.config import save_config, load_config, list_saved_projects
from utils.errors import ConfigLoadError


class TestListSavedProjects:
    """测试 list_saved_projects() 函数 (Story 1.3 任务 1)"""

    def test_empty_directory_returns_empty_list(self):
        """空目录返回空列表（任务 6.1）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                result = list_saved_projects()
                assert result == []
                assert isinstance(result, list)
            finally:
                core.config.CONFIG_DIR = original_dir

    def test_multiple_projects_returned(self):
        """返回多个项目名称列表（任务 6.1）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 创建多个项目配置
                for i in range(3):
                    config = ProjectConfig(
                        name=f"project{i}",
                        simulink_path=f"C:\\Project{i}",
                        matlab_code_path=f"C:\\MATLAB{i}",
                        a2l_path=f"C:\\A2L{i}",
                        target_path=f"C:\\Target{i}",
                        iar_project_path=f"C:\\IAR{i}.eww"
                    )
                    save_config(config, f"project{i}")

                # 列出项目
                result = list_saved_projects()
                assert len(result) == 3
                assert "project0" in result
                assert "project1" in result
                assert "project2" in result
                # 验证排序
                assert result == sorted(result)

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_nonexistent_directory_returns_empty_list(self):
        """目录不存在返回空列表（任务 6.1, 6.4）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            # 指向不存在的子目录
            core.config.CONFIG_DIR = Path(tmpdir) / "nonexistent"

            try:
                result = list_saved_projects()
                assert result == []
            finally:
                core.config.CONFIG_DIR = original_dir

    def test_project_names_without_toml_extension(self):
        """返回的项目名称不含 .toml 后缀（任务 1.3）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                config = ProjectConfig(
                    name="testproject",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )
                save_config(config, "testproject")

                result = list_saved_projects()
                assert "testproject" in result
                assert not any(name.endswith(".toml") for name in result)

            finally:
                core.config.CONFIG_DIR = original_dir


class TestLoadProjectConfig:
    """测试 load_config() 函数增强行为 (Story 1.3 任务 2, 3)

    Code Review Fixes (2026-02-06): Updated to expect ConfigLoadError
    """

    def test_successful_load(self):
        """成功加载配置（任务 6.2）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 先保存配置
                original = ProjectConfig(
                    name="test_project",
                    simulink_path="C:\\Simulink",
                    matlab_code_path="C:\\MATLAB",
                    a2l_path="C:\\A2L",
                    target_path="C:\\Target",
                    iar_project_path="C:\\IAR.eww",
                    description="测试项目"
                )
                save_config(original, "test_project")

                # 加载配置
                loaded = load_config("test_project")

                assert loaded is not None
                assert loaded.name == "test_project"
                assert loaded.simulink_path == "C:\\Simulink"
                assert loaded.matlab_code_path == "C:\\MATLAB"
                assert loaded.a2l_path == "C:\\A2L"
                assert loaded.target_path == "C:\\Target"
                assert loaded.iar_project_path == "C:\\IAR.eww"
                assert loaded.description == "测试项目"

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_load_nonexistent_file_raises_error(self):
        """加载不存在的文件抛出 ConfigLoadError（任务 6.2，代码审查修复）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 期望抛出 ConfigLoadError 而不是返回 None
                with pytest.raises(ConfigLoadError) as exc_info:
                    load_config("nonexistent_project")

                # 验证错误消息包含建议
                assert "不存在" in str(exc_info.value)
                assert len(exc_info.value.suggestions) > 0

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_load_with_missing_required_field_raises_error(self):
        """加载缺失必填字段的配置抛出 ConfigLoadError（任务 6.3，代码审查修复）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 手动创建不完整的 TOML 文件（使用英文避免编码问题）
                config_file = Path(tmpdir) / "incomplete.toml"
                config_file.write_text('''
name = "incomplete"
simulink_path = "C:\\\\Test"
# Missing other required fields
                ''')

                # 期望抛出 ConfigLoadError
                with pytest.raises(ConfigLoadError) as exc_info:
                    load_config("incomplete")

                # 验证错误消息包含"incomplete"（检查字段缺失）
                error_str = str(exc_info.value)
                assert "incomplete" in error_str or "不完整" in error_str
                assert len(exc_info.value.suggestions) > 0

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_load_with_empty_required_field_raises_error(self):
        """加载必填字段为空的配置抛出 ConfigLoadError（任务 6.3，代码审查修复）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 手动创建有空字段的 TOML 文件（绕过 save_config 验证）
                config_file = Path(tmpdir) / "empty_fields.toml"
                config_file.write_text("""
name = "empty_fields"
simulink_path = ""
matlab_code_path = ""
a2l_path = ""
target_path = ""
iar_project_path = ""
                """)

                # 验证应该抛出 ConfigLoadError（空字段验证）
                with pytest.raises(ConfigLoadError) as exc_info:
                    load_config("empty_fields")

                assert "不完整" in str(exc_info.value)

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_load_with_invalid_toml_raises_error(self):
        """加载格式错误的 TOML 文件抛出 ConfigLoadError（任务 6.2，代码审查修复）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 手动创建无效的 TOML 文件
                config_file = Path(tmpdir) / "invalid.toml"
                config_file.write_text("this is not valid toml [[[[")

                # 期望抛出 ConfigLoadError
                with pytest.raises(ConfigLoadError) as exc_info:
                    load_config("invalid")

                # 验证错误消息包含"格式错误"
                assert "格式错误" in str(exc_info.value)
                assert len(exc_info.value.suggestions) > 0

            finally:
                core.config.CONFIG_DIR = original_dir


class TestErrorHandling:
    """测试错误处理和友好性（任务 6.5）

    Code Review Fixes (2026-02-06): Updated to test ConfigLoadError suggestions
    """

    def test_friendly_error_messages_with_suggestions(self):
        """验证错误消息的友好性（任务 6.5，代码审查修复）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 测试不存在的配置 - 应抛出 ConfigLoadError
                with pytest.raises(ConfigLoadError) as exc_info:
                    load_config("missing")

                # 验证错误消息是友好的且包含建议
                error = exc_info.value
                assert error.suggestions  # 应该有修复建议
                assert len(error.suggestions) > 0  # 至少有一条建议

                # 验证 __str__ 方法包含建议
                error_str = str(error)
                assert "建议" in error_str

            finally:
                core.config.CONFIG_DIR = original_dir
