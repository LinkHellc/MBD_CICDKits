"""Unit tests for configuration save functionality (Story 1.2).

Tests cover:
- Saving to non-existent directory (AC #4)
- Overwriting existing config files (AC #5)
- Filename sanitization
- Timestamp generation
"""

import tempfile
from pathlib import Path
from datetime import datetime
import pytest

from core.models import ProjectConfig
from core.config import save_config, config_exists, get_config_dir


class TestConfigSave:
    """测试配置保存功能"""

    def test_save_to_nonexistent_directory(self):
        """测试保存到不存在的目录（AC #4）

        Given: 配置目录不存在
        When: 保存配置
        Then: 目录应自动创建，保存成功
        """
        import core.config
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            # 临时替换配置目录为不存在的子目录
            test_dir = Path(tmpdir) / "subdir" / "configs"
            core.config.CONFIG_DIR = test_dir

            try:
                config = ProjectConfig(
                    name="test_project",
                    simulink_path="C:\\Projects\\Test",
                    matlab_code_path="C:\\MATLAB\\code",
                    a2l_path="C:\\A2L",
                    target_path="C:\\Target",
                    iar_project_path="C:\\IAR\\test.eww"
                )

                # 保存应该自动创建目录
                result = save_config(config, "test_project", overwrite=True)
                assert result is True
                assert test_dir.exists()
                assert config_exists("test_project") is True

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_overwrite_existing_config(self):
        """测试覆盖已存在的配置（AC #5）

        Given: 配置文件已存在
        When: 使用 overwrite=True 保存同名配置
        Then: 旧配置应被新配置覆盖
        """
        import core.config
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 第一次保存
                config1 = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Old",
                    matlab_code_path="C:\\Old",
                    a2l_path="C:\\Old",
                    target_path="C:\\Old",
                    iar_project_path="C:\\Old.eww"
                )
                result1 = save_config(config1, "test", overwrite=True)
                assert result1 is True

                # 检查文件存在
                assert config_exists("test") is True

                # 第二次保存（覆盖）
                config2 = ProjectConfig(
                    name="test",
                    simulink_path="C:\\New",
                    matlab_code_path="C:\\New",
                    a2l_path="C:\\New",
                    target_path="C:\\New",
                    iar_project_path="C:\\New.eww"
                )
                result2 = save_config(config2, "test", overwrite=True)
                assert result2 is True

                # 验证覆盖成功：读取文件确认内容已更新
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib

                config_file = Path(tmpdir) / "test.toml"
                assert config_file.exists()

                with open(config_file, "rb") as f:
                    loaded = tomllib.load(f)

                # 验证内容已被新值覆盖
                assert loaded["simulink_path"] == "C:\\New"
                assert loaded["matlab_code_path"] == "C:\\New"
                assert loaded["a2l_path"] == "C:\\New"
                assert loaded["target_path"] == "C:\\New"
                assert loaded["iar_project_path"] == "C:\\New.eww"

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_save_without_overwrite_returns_false(self):
        """测试不覆盖模式（overwrite=False）

        Given: 配置文件已存在
        When: 使用 overwrite=False（默认）保存
        Then: 应返回 False，文件不被覆盖
        """
        import core.config
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 第一次保存
                config1 = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Old",
                    matlab_code_path="C:\\Old",
                    a2l_path="C:\\Old",
                    target_path="C:\\Old",
                    iar_project_path="C:\\Old.eww"
                )
                save_config(config1, "test", overwrite=True)

                # 第二次保存（不覆盖）
                config2 = ProjectConfig(
                    name="test",
                    simulink_path="C:\\New",
                    matlab_code_path="C:\\New",
                    a2l_path="C:\\New",
                    target_path="C:\\New",
                    iar_project_path="C:\\New.eww"
                )
                result = save_config(config2, "test", overwrite=False)
                assert result is False

            finally:
                core.config.CONFIG_DIR = original_dir


class TestSanitizeFilename:
    """测试文件名清理功能"""

    def test_sanitize_filename_removes_illegal_chars(self):
        """测试移除非法字符"""
        from utils.path_utils import sanitize_filename

        # 非法字符被替换
        assert sanitize_filename("test<file>name") == "test_file_name"
        assert sanitize_filename('test:file/name?') == "test_file_name_"
        assert sanitize_filename('test"file|name*') == "test_file_name_"

    def test_sanitize_filename_trims_whitespace_and_dots(self):
        """测试移除首尾空格和点"""
        from utils.path_utils import sanitize_filename

        # 首尾空格和点被移除
        assert sanitize_filename("  .test.  ") == "test"
        assert sanitize_filename("...test...") == "test"

    def test_sanitize_filename_length_limit(self):
        """测试长度限制"""
        from utils.path_utils import sanitize_filename

        # 长度限制
        long_name = "a" * 100
        result = sanitize_filename(long_name)
        assert len(result) == 50

    def test_sanitize_filename_empty_returns_default(self):
        """测试空字符串返回默认值"""
        from utils.path_utils import sanitize_filename

        # 空字符串返回默认值
        assert sanitize_filename("") == "unnamed_project"
        assert sanitize_filename("   ") == "unnamed_project"
        # 只有非法字符的情况
        assert sanitize_filename("<>:\"/\\|?*") == "unnamed_project"


class TestTimestampGeneration:
    """测试时间戳生成功能"""

    def test_timestamp_generation_on_save(self):
        """测试保存时生成时间戳

        Given: 新配置对象没有时间戳
        When: 保存配置
        Then: created_at 和 modified_at 应被自动设置
        """
        import core.config
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                config = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )

                # 初始状态没有时间戳
                assert config.created_at == ""
                assert config.modified_at == ""

                # 保存配置
                save_config(config, "test", overwrite=True)

                # 验证时间戳已设置
                assert config.created_at != ""
                assert config.modified_at != ""

                # 验证时间戳格式（ISO 8601）
                datetime.fromisoformat(config.created_at)
                datetime.fromisoformat(config.modified_at)

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_modified_at_updates_on_resave(self):
        """测试重复保存时 modified_at 更新

        Given: 已存在的配置
        When: 再次保存
        Then: modified_at 应更新，created_at 保持不变
        """
        import core.config
        import time
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                config = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )

                # 第一次保存
                save_config(config, "test", overwrite=True)
                first_created = config.created_at
                first_modified = config.modified_at

                # 等待一小段时间确保时间戳不同
                time.sleep(0.01)

                # 第二次保存
                save_config(config, "test", overwrite=True)
                second_created = config.created_at
                second_modified = config.modified_at

                # created_at 不应改变
                assert second_created == first_created
                # modified_at 应该更新
                assert second_modified != first_modified

            finally:
                core.config.CONFIG_DIR = original_dir


class TestConfigExists:
    """测试 config_exists 函数"""

    def test_config_exists_returns_true_for_existing(self):
        """测试存在的配置返回 True"""
        import core.config
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                config = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )
                save_config(config, "test", overwrite=True)

                assert config_exists("test") is True

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_config_exists_returns_false_for_nonexistent(self):
        """测试不存在的配置返回 False"""
        assert config_exists("nonexistent") is False

    def test_config_exists_returns_false_for_empty(self):
        """测试空字符串返回 False"""
        assert config_exists("") is False


class TestTOMLFormat:
    """测试生成的 TOML 文件格式"""

    def test_saved_config_is_valid_toml(self):
        """测试保存的配置文件是有效的 TOML 格式

        Given: 一个有效的配置对象
        When: 保存到文件
        Then: 生成的文件应该是有效的 TOML 格式且可重新加载
        """
        import core.config
        original_dir = core.config.CONFIG_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                original_config = ProjectConfig(
                    name="test_format",
                    description="Test description",
                    simulink_path="C:\\Simulink\\Test",
                    matlab_code_path="C:\\MATLAB\\code",
                    a2l_path="C:\\A2L",
                    target_path="C:\\Target",
                    iar_project_path="C:\\IAR\\test.eww"
                )

                # 保存配置
                result = save_config(original_config, "test_format", overwrite=True)
                assert result is True

                # 验证文件存在
                config_file = Path(tmpdir) / "test_format.toml"
                assert config_file.exists()

                # 验证可以重新加载为有效的 TOML
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib

                with open(config_file, "rb") as f:
                    loaded_dict = tomllib.load(f)

                # 验证加载的内容与原始配置匹配
                assert loaded_dict["name"] == "test_format"
                assert loaded_dict["description"] == "Test description"
                assert loaded_dict["simulink_path"] == "C:\\Simulink\\Test"
                assert loaded_dict["matlab_code_path"] == "C:\\MATLAB\\code"
                assert loaded_dict["a2l_path"] == "C:\\A2L"
                assert loaded_dict["target_path"] == "C:\\Target"
                assert loaded_dict["iar_project_path"] == "C:\\IAR\\test.eww"

            finally:
                core.config.CONFIG_DIR = original_dir
