"""Path and filename utility functions for MBD_CICDKits.

This module provides utilities for sanitizing filenames and handling paths
in a cross-platform manner.
"""

import re


def sanitize_filename(name: str, max_length: int = 50) -> str:
    r"""清理文件名中的非法字符

    移除 Windows 非法字符: < > : " / \ | ? *
    限制文件名长度为 max_length 字符
    去除首尾空格和点

    Args:
        name: 原始文件名
        max_length: 最大长度限制（默认 50）

    Returns:
        清理后的文件名，如果清理后为空则返回 "unnamed_project"

    Examples:
        >>> sanitize_filename("test<file>name")
        'test_file_name'
        >>> sanitize_filename("  .test.  ")
        'test'
        >>> sanitize_filename("")
        'unnamed_project'
    """
    if not name:
        return "unnamed_project"

    # 移除 Windows 非法字符: < > : " / \ | ? *
    # 以及控制字符 (0-31)
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    cleaned = re.sub(illegal_chars, '_', name)

    # 去除首尾空格和点
    cleaned = cleaned.strip('. ')

    # 限制长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()

    # 如果清理后为空或只包含下划线，返回默认名称
    if not cleaned or cleaned == '_' * len(cleaned):
        cleaned = "unnamed_project"

    return cleaned
