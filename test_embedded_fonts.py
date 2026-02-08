#!/usr/bin/env python
"""测试嵌入字体加载功能"""

import sys
sys.path.insert(0, "src")

from PyQt6.QtWidgets import QApplication
from ui.styles.industrial_theme import FontManager, BrandColors


def main():
    app = QApplication([])

    print("=" * 60)
    print("MBD_CICDKits 嵌入字体测试")
    print("=" * 60)

    # 加载嵌入字体
    print("\n[加载嵌入字体]")
    FontManager._load_embedded_fonts()
    print("  嵌入字体加载完成")

    # 检查字体可用性
    print("\n[字体可用性检查]")
    font_info = FontManager.get_font_info()
    for font_name, available in font_info.items():
        status = "[+]" if available else "[ ]"
        print(f"  {font_name:20s} {status}")

    # 测试字体获取
    print("\n[字体对象测试]")
    heading_font = FontManager.get_heading_font(24)
    body_font = FontManager.get_body_font(14)

    print(f"  标题字体: {heading_font.family()}")
    print(f"  正文字体: {body_font.family()}")

    # 检查品牌配色
    print("\n[品牌配色检查]")
    print(f"  主强调色: {BrandColors.ACCENT_PRIMARY}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
