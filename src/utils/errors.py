"""Unified error classes for MBD_CICDKits.

This module provides exception classes with helpful suggestions
for resolving configuration errors.
"""

from typing import List


class ConfigError(Exception):
    """配置相关错误基类

    提供错误消息和可操作的修复建议。
    """

    def __init__(self, message: str, suggestions: List[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

    def __str__(self):
        base_msg = super().__str__()
        if self.suggestions:
            suggestions = "\n".join(f"  - {s}" for s in self.suggestions)
            return f"{base_msg}\n\n建议:\n{suggestions}"
        return base_msg


class ConfigSaveError(ConfigError):
    """配置保存失败

    当无法保存配置到文件系统时抛出。
    """

    def __init__(self, reason: str):
        super().__init__(
            f"无法保存配置: {reason}",
            suggestions=[
                "检查配置目录权限",
                "确保磁盘空间充足",
                "查看详细日志获取更多信息"
            ]
        )


class ConfigValidationError(ConfigError):
    """配置验证失败

    当配置不符合验证规则时抛出。
    """

    def __init__(self, message: str, suggestions: List[str] = None):
        default_suggestions = [
            "检查所有必填字段是否已填写",
            "确保路径格式正确",
            "查看配置表单中的红色提示"
        ]
        if suggestions:
            default_suggestions.extend(suggestions)
        super().__init__(message, default_suggestions)


class ConfigLoadError(ConfigError):
    """配置加载失败

    当无法从文件加载配置时抛出。
    Code Review Fixes (2026-02-06): 添加自定义 suggestions 支持
    """

    def __init__(self, reason: str, suggestions: List[str] = None):
        default_suggestions = [
            "检查配置文件是否存在",
            "验证文件格式是否正确",
            "确保文件没有被其他程序锁定"
        ]
        if suggestions:
            default_suggestions = suggestions  # 使用自定义建议替代默认建议
        super().__init__(
            f"无法加载配置: {reason}",
            default_suggestions
        )
