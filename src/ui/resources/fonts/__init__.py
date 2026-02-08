"""
字体资源模块

该模块负责加载和管理应用内嵌字体。

字体来源：
1. 应用资源目录 (src/ui/resources/fonts/)
2. 用户数据目录
3. 系统字体（降级）
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtGui import QFontDatabase


class FontLoader:
    """字体加载器 - 从文件加载字体到 QFontDatabase"""

    # 字体文件配置
    FONT_FILES = {
        "Poppins": {
            "regular": "Poppins-Regular.ttf",
            "bold": "Poppins-Bold.ttf",
        },
        "Lora": {
            "regular": "Lora-Regular.ttf",
            "bold": "Lora-Bold.ttf",
        }
    }

    # 下载 URL
    DOWNLOAD_URLS = {
        "Poppins-Regular": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
        "Poppins-Bold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
        "Lora-Regular": "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Regular.ttf",
        "Lora-Bold": "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Bold.ttf",
    }

    def __init__(self):
        """初始化字体加载器"""
        self._loaded_families: dict[str, str] = {}
        self._font_dirs: list[Path] = []

        # 添加字体目录
        self._add_font_directories()

    def _add_font_directories(self) -> None:
        """添加字体搜索目录"""
        # 1. 应用资源目录
        resource_dir = Path(__file__).parent
        self._font_dirs.append(resource_dir)

        # 2. 用户数据目录
        import os
        user_font_dir = Path(os.path.expanduser("~")) / ".mbd_cicdkits" / "fonts"
        self._font_dirs.append(user_font_dir)

    def load_font(self, family: str, weight: str = "regular") -> Optional[str]:
        """加载字体文件

        Args:
            family: 字体名称 (如 "Poppins", "Lora")
            weight: 字体粗细 ("regular" 或 "bold")

        Returns:
            加载成功返回字体家族名称，失败返回 None
        """
        if family in self._loaded_families:
            return self._loaded_families[family]

        if family not in self.FONT_FILES:
            return None

        filename = self.FONT_FILES[family].get(weight, self.FONT_FILES[family]["regular"])

        # 搜索字体文件
        for font_dir in self._font_dirs:
            font_path = font_dir / filename
            if font_path.exists():
                try:
                    font_id = QFontDatabase.addApplicationFont(str(font_path))
                    if font_id >= 0:
                        # 获取实际的字体家族名称
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        if families:
                            self._loaded_families[family] = families[0]
                            return families[0]
                except Exception as e:
                    print(f"加载字体失败 {font_path}: {e}")

        return None

    def load_all_fonts(self) -> dict[str, bool]:
        """加载所有配置的字体

        Returns:
            字体名称到加载状态的映射
        """
        results = {}

        for family in self.FONT_FILES:
            # 尝试加载 regular 字体
            loaded = self.load_font(family, "regular") is not None
            results[family] = loaded

            if loaded:
                # 也加载 bold 变体
                self.load_font(family, "bold")

        return results

    def get_font_family(self, family: str) -> Optional[str]:
        """获取加载后的字体家族名称

        Args:
            family: 原始字体名称

        Returns:
            加载后的字体家族名称，如果未加载返回原始名称
        """
        if family in self._loaded_families:
            return self._loaded_families[family]
        return None

    @staticmethod
    def get_download_script() -> str:
        """获取字体下载脚本内容"""
        return '''#!/usr/bin/env python3
"""MBD_CICDKits 字体下载脚本

自动下载 Poppins 和 Lora 字体到用户字体目录。
"""

import os
import urllib.request
from pathlib import Path


def download_file(url: str, dest: Path) -> bool:
    """下载文件"""
    try:
        print(f"下载: {os.path.basename(dest)}")
        urllib.request.urlretrieve(url, dest)
        print(f"  完成: {dest}")
        return True
    except Exception as e:
        print(f"  失败: {e}")
        return False


def main():
    # 创建字体目录
    font_dir = Path.home() / ".mbd_cicdkits" / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)

    print("MBD_CICDKits 字体下载器")
    print("=" * 50)
    print(f"目标目录: {font_dir}")
    print()

    # 字体下载列表
    fonts = [
        ("Poppins-Regular", "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf"),
        ("Poppins-Bold", "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"),
        ("Lora-Regular", "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Regular.ttf"),
        ("Lora-Bold", "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Bold.ttf"),
    ]

    success = 0
    for name, url in fonts:
        dest = font_dir / f"{name}.ttf"
        if dest.exists():
            print(f"[跳过] {name}.ttf 已存在")
            success += 1
        elif download_file(url, dest):
            success += 1
        print()

    print("=" * 50)
    print(f"完成: {success}/{len(fonts)} 个字体文件")


if __name__ == "__main__":
    main()
'''


# 全局字体加载器实例
_font_loader: Optional[FontLoader] = None


def get_font_loader() -> FontLoader:
    """获取全局字体加载器实例"""
    global _font_loader
    if _font_loader is None:
        _font_loader = FontLoader()
    return _font_loader


def initialize_fonts() -> dict[str, bool]:
    """初始化所有应用字体

    Returns:
        字体名称到加载状态的映射
    """
    loader = get_font_loader()
    return loader.load_all_fonts()
