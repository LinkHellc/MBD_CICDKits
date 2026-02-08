#!/usr/bin/env python
"""测试 Poppins 字体加载"""

import sys
sys.path.insert(0, "src")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from pathlib import Path


def main():
    app = QApplication([])

    print("=" * 60)
    print("MBD_CICDKits Poppins 字体测试")
    print("=" * 60)

    font_dir = Path("src/ui/resources/fonts")

    # 检查字体文件
    print("\n[字体文件检查]")
    for font_file in ["Poppins-Regular.ttf", "Poppins-Bold.ttf", "Lora-Regular.ttf", "Lora-Bold.ttf"]:
        path = font_dir / font_file
        status = "[+]" if path.exists() else "[ ]"
        size = f"{path.stat().st_size / 1024:.1f}KB" if path.exists() else "N/A"
        print(f"  {font_file:20s} {status} {size}")

    # 加载 Poppins 字体
    print("\n[加载 Poppins 字体]")
    regular_path = font_dir / "Poppins-Regular.ttf"
    bold_path = font_dir / "Poppins-Bold.ttf"

    loaded_fonts = []

    if regular_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(regular_path))
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                loaded_fonts.append(families[0])
                print(f"  Poppins-Regular: {families[0]}")
            else:
                print("  Poppins-Regular: No families found")
        else:
            print("  Poppins-Regular: Load failed")
    else:
        print("  Poppins-Regular: File not found")

    if bold_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(bold_path))
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                print(f"  Poppins-Bold: {families[0]}")
            else:
                print("  Poppins-Bold: No families found")
        else:
            print("  Poppins-Bold: Load failed")

    # 检查 Poppins 是否可用
    print("\n[字体可用性检查]")
    all_fonts = QFontDatabase.families()
    print(f"  Poppins in system: {'Poppins' in all_fonts}")
    print(f"  Total fonts loaded: {len(all_fonts)}")

    # 查找包含 Poppins 的字体
    poppins_fonts = [f for f in all_fonts if 'Poppins' in f]
    if poppins_fonts:
        print(f"  Found Poppins variants:")
        for f in poppins_fonts[:5]:  # 只显示前5个
            print(f"    - {f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
