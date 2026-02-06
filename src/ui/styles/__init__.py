"""
UI 样式模块

包含 MBD_CICDKits 的主题系统。
"""

from .industrial_theme import (
    Colors,
    LightColors,
    apply_industrial_theme,
    set_theme,
    get_colors
)

__all__ = [
    'Colors',
    'LightColors',
    'apply_industrial_theme',
    'set_theme',
    'get_colors'
]
