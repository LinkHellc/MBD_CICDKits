"""Unit tests for configuration module."""

import pytest
import tempfile
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.models import ProjectConfig
from core.config import save_config, load_config, list_configs, delete_config, update_config
from utils.errors import ConfigError, ConfigValidationError, ConfigLoadError


def test_project_config_defaults():
    """测试配置模型默认值"""
    config = ProjectConfig()
    assert config.name == ""
    assert config.simulink_path == ""
    assert config.matlab_code_path == ""
    assert config.a2l_path == ""
    assert config.target_path == ""
    assert config.iar_project_path == ""


def test_project_config_creation():
    """测试配置对象创建"""
    config = ProjectConfig(
        name="test_project",
        simulink_path="C:\\Projects\\Test",
        matlab_code_path="C:\\MATLAB\\code",
        a2l_path="C:\\A2L",
        target_path="C:\\Target",
        iar_project_path="C:\\IAR\\project.eww",
    )
    assert config.name == "test_project"
    assert config.simulink_path == "C:\\Projects\\Test"


def test_project_config_to_dict():
    """测试配置转换为字典"""
    config = ProjectConfig(
        name="test", simulink_path="C:\\Test", matlab_code_path="C:\\MATLAB"
    )
    data = config.to_dict()
    assert data["name"] == "test"
    assert data["simulink_path"] == "C:\\Test"


def test_project_config_from_dict():
    """测试从字典创建配置"""
    data = {
        "name": "test",
        "simulink_path": "C:\\Test",
        "matlab_code_path": "C:\\MATLAB",
    }
    config = ProjectConfig.from_dict(data)
    assert config.name == "test"
    assert config.simulink_path == "C:\\Test"


def test_validate_required_fields_empty():
    """测试空字段验证"""
    config = ProjectConfig()
    errors = config.validate_required_fields()
    assert len(errors) == 6  # 6个必填字段（包括 name）


def test_validate_required_fields_valid():
    """测试有效字段验证"""
    config = ProjectConfig(
        name="test_project",  # 添加 name 字段
        simulink_path="C:\\Test",
        matlab_code_path="C:\\MATLAB",
        a2l_path="C:\\A2L",
        target_path="C:\\Target",
        iar_project_path="C:\\IAR",
    )
    errors = config.validate_required_fields()
    assert len(errors) == 0


def test_save_and_load_config():
    """测试配置保存和加载"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 修改 CONFIG_DIR 指向临时目录
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建测试配置
            config = ProjectConfig(
                name="test_project",
                simulink_path="C:\\Projects\\Test",
                matlab_code_path="C:\\MATLAB\\code",
                a2l_path="C:\\A2L",
                target_path="C:\\Target",
                iar_project_path="C:\\IAR\\project.eww",
            )

            # 保存
            assert save_config(config, "test_project") is True

            # 验证文件存在
            config_file = Path(tmpdir) / "test_project.toml"
            assert config_file.exists()

            # 加载
            loaded = load_config("test_project")
            assert loaded is not None
            assert loaded.name == "test_project"
            assert loaded.simulink_path == "C:\\Projects\\Test"
            assert loaded.matlab_code_path == "C:\\MATLAB\\code"

        finally:
            core.config.CONFIG_DIR = original_dir


def test_load_nonexistent_config():
    """测试加载不存在的配置（应抛出 ConfigLoadError）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # load_config 现在抛出 ConfigLoadError 而非返回 None
            with pytest.raises(ConfigLoadError):
                load_config("nonexistent")

        finally:
            core.config.CONFIG_DIR = original_dir


def test_list_configs():
    """测试列出配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建几个配置文件（包含所有必填字段）
            config1 = ProjectConfig(
                name="project1",
                simulink_path="C:\\P1",
                matlab_code_path="C:\\P1",
                a2l_path="C:\\P1",
                target_path="C:\\P1",
                iar_project_path="C:\\P1.eww"
            )
            config2 = ProjectConfig(
                name="project2",
                simulink_path="C:\\P2",
                matlab_code_path="C:\\P2",
                a2l_path="C:\\P2",
                target_path="C:\\P2",
                iar_project_path="C:\\P2.eww"
            )

            save_config(config1, "project1")
            save_config(config2, "project2")

            # 列出配置
            configs = list_configs()
            assert "project1" in configs
            assert "project2" in configs

        finally:
            core.config.CONFIG_DIR = original_dir


def test_delete_config():
    """测试删除配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建配置（包含所有必填字段）
            config = ProjectConfig(
                name="to_delete",
                simulink_path="C:\\Test",
                matlab_code_path="C:\\Test",
                a2l_path="C:\\Test",
                target_path="C:\\Test",
                iar_project_path="C:\\Test.eww"
            )
            save_config(config, "to_delete")

            # 验证存在
            config_file = Path(tmpdir) / "to_delete.toml"
            assert config_file.exists()

            # 删除
            assert delete_config("to_delete") is True
            assert not config_file.exists()

            # 删除不存在的配置
            assert delete_config("nonexistent") is False

        finally:
            core.config.CONFIG_DIR = original_dir


class TestUpdateConfig:
    """测试配置更新功能 (Story 1.4)"""

    def test_successful_update(self):
        """成功更新配置

        Given: 已存在的项目配置
        When: 使用新路径调用 update_config
        Then: 配置应被更新，modified_at 时间戳更新
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config

            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 先创建原始配置
                original = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Old\\Simulink",
                    matlab_code_path="C:\\Old\\MATLAB",
                    a2l_path="C:\\Old\\A2L",
                    target_path="C:\\Old\\Target",
                    iar_project_path="C:\\Old\\IAR.eww"
                )
                save_config(original, "test", overwrite=True)
                first_modified = original.modified_at

                # 更新配置
                updated = ProjectConfig(
                    name="test",
                    simulink_path="C:\\New\\Simulink",
                    matlab_code_path="C:\\New\\MATLAB",
                    a2l_path="C:\\New\\A2L",
                    target_path="C:\\New\\Target",
                    iar_project_path="C:\\New\\IAR.eww"
                )
                result = update_config("test", updated)

                assert result is True
                assert updated.modified_at != ""

                # 验证更新后的配置
                loaded = load_config("test")
                assert loaded is not None
                assert loaded.simulink_path == "C:\\New\\Simulink"
                assert loaded.matlab_code_path == "C:\\New\\MATLAB"

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_update_nonexistent_project(self):
        """更新不存在的项目应抛出 ConfigError

        Given: 不存在的项目名称
        When: 调用 update_config
        Then: 应抛出 ConfigError
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config

            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                config = ProjectConfig(
                    name="nonexistent",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )

                with pytest.raises(ConfigError):
                    update_config("nonexistent", config)

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_update_with_invalid_config(self):
        """更新时验证失败应抛出 ConfigValidationError

        Given: 必填字段为空的配置
        When: 调用 update_config
        Then: 应抛出 ConfigValidationError
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config

            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 先创建原始配置
                original = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Old",
                    matlab_code_path="C:\\Old",
                    a2l_path="C:\\Old",
                    target_path="C:\\Old",
                    iar_project_path="C:\\Old.eww"
                )
                save_config(original, "test", overwrite=True)

                # 尝试用无效配置更新
                invalid = ProjectConfig(
                    name="test",
                    simulink_path="",  # 空路径
                    matlab_code_path="",
                    a2l_path="",
                    target_path="",
                    iar_project_path=""
                )

                with pytest.raises(ConfigValidationError):
                    update_config("test", invalid)

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_update_preserves_created_at(self):
        """更新时 created_at 时间戳应保持不变

        Given: 已存在的项目配置
        When: 调用 update_config
        Then: created_at 应保持不变，modified_at 应更新
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            import time

            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 创建原始配置
                original = ProjectConfig(
                    name="test",
                    simulink_path="C:\\Old",
                    matlab_code_path="C:\\Old",
                    a2l_path="C:\\Old",
                    target_path="C:\\Old",
                    iar_project_path="C:\\Old.eww"
                )
                save_config(original, "test", overwrite=True)
                original_created = original.created_at

                # 等待确保时间戳不同
                time.sleep(0.01)

                # 更新配置
                updated = ProjectConfig(
                    name="test",
                    simulink_path="C:\\New",
                    matlab_code_path="C:\\New",
                    a2l_path="C:\\New",
                    target_path="C:\\New",
                    iar_project_path="C:\\New.eww"
                )
                update_config("test", updated)

                # 验证 created_at 不变
                assert updated.created_at == original_created
                # modified_at 应该更新
                assert updated.modified_at != original.modified_at

            finally:
                core.config.CONFIG_DIR = original_dir
