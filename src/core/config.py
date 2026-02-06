"""Configuration persistence module for MBD_CICDKits.

This module handles saving and loading project configurations in TOML format
following Architecture Decision 1.1 (Configuration Format: TOML).
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Python 3.11+ has built-in tomllib, Python 3.10 needs tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib

# tomli_w is needed for writing TOML
try:
    import tomli_w
except ImportError:
    tomli_w = None

from core.models import ProjectConfig
from utils.errors import (
    ConfigSaveError,
    ConfigValidationError,
    ConfigLoadError,
    ConfigError
)

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """获取平台相关的配置目录

    遵循 AC #1: 保存到 %APPDATA%/MBD_CICDKits/projects/ (Windows)
    或 ~/.config/mbd_cicdkits/projects/ (Linux/macOS)

    Returns:
        平台相关的配置目录路径
    """
    if sys.platform == "win32":  # Windows
        return Path.home() / "AppData" / "Roaming" / "MBD_CICDKits" / "projects"
    else:  # macOS/Linux
        return Path.home() / ".config" / "mbd_cicdkits" / "projects"


# 配置存储位置
CONFIG_DIR = get_config_dir()


def get_projects_dir() -> Path:
    """获取项目配置目录（get_config_dir 的别名）

    为了代码清晰性，提供更语义化的函数名。

    Returns:
        项目配置目录路径（与 get_config_dir 相同）
    """
    return get_config_dir()


def save_config(config: ProjectConfig, filename: str, overwrite: bool = False) -> bool:
    """保存项目配置到 TOML 文件

    Args:
        config: 项目配置对象
        filename: 文件名（不含扩展名）
        overwrite: 是否覆盖已存在的文件（默认 False）

    Returns:
        bool: 保存是否成功

    Raises:
        ConfigValidationError: 配置验证失败时抛出
        ConfigSaveError: 保存失败时抛出
    """
    if tomli_w is None:
        logger.error("tomli_w 未安装，请运行: pip install tomli_w")
        raise ConfigSaveError("tomli_w 未安装")

    try:
        # 使用 CONFIG_DIR 常量（与 load_config 保持一致）
        config_dir = CONFIG_DIR

        # 确保配置目录存在（AC #4）
        config_dir.mkdir(parents=True, exist_ok=True)

        # 验证配置（Story 1.2: 保存前验证）
        errors = config.validate_required_fields()
        if errors:
            raise ConfigValidationError(
                f"配置验证失败: {', '.join(errors)}",
                suggestions=["检查所有必填字段是否已填写"]
            )

        # 检查文件是否存在（AC #5）
        config_file = config_dir / f"{filename}.toml"
        if config_file.exists() and not overwrite:
            return False  # 通知UI层显示确认对话框

        # 更新时间戳（Story 1.2: 添加 created_at 和 modified_at）
        now = datetime.now().isoformat()
        config.modified_at = now
        if not config.created_at:
            config.created_at = now

        # 转换为字典（排除 None 值和空字符串）
        config_dict = config.to_dict()

        # 保存为 TOML
        with open(config_file, "wb") as f:
            tomli_w.dump(config_dict, f)

        logger.info(f"配置已保存: {filename}")
        return True

    except ConfigValidationError:
        raise
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        raise ConfigSaveError(str(e))


def config_exists(filename: str) -> bool:
    """检查配置文件是否存在

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        bool: 文件是否存在
    """
    if not filename:
        return False
    config_file = get_config_dir() / f"{filename}.toml"
    return config_file.exists()


def load_config(filename: str) -> Optional[ProjectConfig]:
    """加载项目配置

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        ProjectConfig 对象

    Raises:
        ConfigLoadError: 配置文件不存在、格式错误或验证失败时抛出
    """
    try:
        config_file = CONFIG_DIR / f"{filename}.toml"

        if not config_file.exists():
            raise ConfigLoadError(
                f"配置文件不存在: {filename}",
                suggestions=[
                    f"检查项目名称 '{filename}' 是否正确",
                    "重新创建项目配置",
                    "查看已保存的项目列表"
                ]
            )

        try:
            with open(config_file, "rb") as f:
                config_dict = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigLoadError(
                f"配置文件格式错误: {filename}",
                suggestions=[
                    "使用文本编辑器检查 TOML 文件格式",
                    "从备份恢复配置文件",
                    "重新创建项目配置"
                ]
            )

        config = ProjectConfig.from_dict(config_dict)

        # 验证必需字段
        errors = config.validate_required_fields()
        if errors:
            raise ConfigLoadError(
                f"配置信息不完整: {', '.join(errors)}",
                suggestions=[
                    "重新创建项目配置",
                    "手动编辑配置文件补充缺失字段",
                    "检查配置文件完整性"
                ]
            )

        logger.info(f"配置已加载: {filename}")
        return config

    except ConfigLoadError:
        raise
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        raise ConfigLoadError(str(e))


def list_configs() -> list[str]:
    """列出所有已保存的配置文件

    Returns:
        配置文件名列表（不含扩展名）
    """
    try:
        if not CONFIG_DIR.exists():
            return []

        config_files = []
        for file in CONFIG_DIR.glob("*.toml"):
            config_files.append(file.stem)

        return sorted(config_files)

    except Exception as e:
        logger.error(f"列出配置失败: {e}")
        return []


def list_saved_projects() -> list[str]:
    """列出所有已保存的项目配置（Story 1.3）

    这是 list_configs() 的语义化别名，用于 Story 1.3 加载项目功能。

    Returns:
        项目名称列表（不含扩展名），按字母排序
    """
    return list_configs()


def delete_config(filename: str) -> bool:
    """删除配置文件

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        bool: 删除是否成功
    """
    try:
        config_file = CONFIG_DIR / f"{filename}.toml"

        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            return False

        config_file.unlink()
        logger.info(f"配置已删除: {config_file}")
        return True

    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        return False


def update_config(project_name: str, updated_config: ProjectConfig) -> bool:
    """更新现有项目配置

    Args:
        project_name: 项目名称（文件名，不含扩展名）
        updated_config: 更新后的配置对象

    Returns:
        bool: 更新是否成功

    Raises:
        ConfigLoadError: 原配置不存在时抛出
        ConfigValidationError: 配置验证失败
    """
    try:
        # 验证配置
        errors = updated_config.validate_required_fields()
        if errors:
            raise ConfigValidationError(
                f"配置验证失败: {', '.join(errors)}",
                suggestions=["检查所有必填字段是否已填写"]
            )

        # 加载原配置以保留 created_at
        try:
            original_config = load_config(project_name)
        except ConfigLoadError:
            raise ConfigLoadError(
                f"项目配置不存在: {project_name}",
                suggestions=[
                    "检查项目名称是否正确",
                    "创建新项目配置",
                ]
            )

        # 保留 created_at，更新 modified_at
        updated_config.created_at = original_config.created_at
        updated_config.modified_at = datetime.now().isoformat()

        # 保存更新（覆盖模式）
        return save_config(updated_config, project_name, overwrite=True)

    except (ConfigLoadError, ConfigValidationError):
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise ConfigError(f"更新配置失败: {str(e)}")
