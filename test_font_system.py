#!/usr/bin/env python
"""测试字体系统 - 验证 FontManager 和品牌配色

运行此脚本查看字体可用性信息。
"""

import sys
sys.path.insert(0, "src")

from PyQt6.QtWidgets import QApplication
from ui.styles.industrial_theme import FontManager, BrandColors, BrandLightColors


def main():
    """测试字体系统"""
    app = QApplication([])

    # 首先加载嵌入字体
    FontManager._load_embedded_fonts()

    print("=" * 60)
    print("MBD_CICDKits 字体系统测试")
    print("=" * 60)

    # 测试字体可用性
    print("\n[字体可用性检查]")
    font_info = FontManager.get_font_info()
    for font_name, available in font_info.items():
        status = "[+]" if available else "[ ]"
        print(f"  {font_name:20s} {status}")

    # 测试字体获取
    print("\n[字体对象测试]")
    heading_font = FontManager.get_heading_font(24)
    body_font = FontManager.get_body_font(14)
    chinese_font = FontManager.get_chinese_font(14)
    code_font = FontManager.get_code_font(12)

    print(f"  标题字体: {heading_font.family()} - {heading_font.pointSize()}pt")
    print(f"  正文字体: {body_font.family()} - {body_font.pointSize()}pt")
    print(f"  中文字体: {chinese_font.family()} - {chinese_font.pointSize()}pt")
    print(f"  代码字体: {code_font.family()} - {code_font.pointSize()}pt")

    # 测试品牌配色
    print("\n[Anthropic 品牌配色]")
    print(f"  深色主题主背景: {BrandColors.BG_PRIMARY}")
    print(f"  主强调色(橙色): {BrandColors.ACCENT_PRIMARY}")
    print(f"  次强调色(蓝色): {BrandColors.ACCENT_SECONDARY}")
    print(f"  成功色(绿色): {BrandColors.ACCENT_SUCCESS}")
    print(f"  主文字色: {BrandColors.TEXT_PRIMARY}")

    print("\n[浅色主题]")
    print(f"  浅色主题主背景: {BrandLightColors.BG_PRIMARY}")
    print(f"  主文字色: {BrandLightColors.TEXT_PRIMARY}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

    # 检测 Poppins 和 Lora 是否可用
    print("\n[字体系统状态]")
    if FontManager.is_font_available("Poppins"):
        print("  [+] Poppins 字体已安装 - 标题将使用 Poppins")
    else:
        print("  [ ] Poppins 字体未安装 - 标题将使用 Arial fallback")

    if FontManager.is_font_available("Lora"):
        print("  [+] Lora 字体已安装 - 正文将使用 Lora")
    else:
        print("  [ ] Lora 字体未安装 - 正文将使用 Georgia fallback")


if __name__ == "__main__":
    main()
