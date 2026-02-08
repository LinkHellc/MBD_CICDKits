#!/usr/bin/env python3
"""MBD_CICDKits 字体下载脚本

自动下载 Poppins 和 Lora 字体到应用字体目录。
"""

import os
import sys
from pathlib import Path

try:
    import urllib.request
except ImportError:
    print("请使用 Python 3 运行此脚本")
    sys.exit(1)


def download_file(url: str, dest: Path) -> bool:
    """下载文件"""
    try:
        print(f"下载: {dest.name}")
        # 使用请求头模拟浏览器
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        # 使用 urlopen 并手动写入文件
        with urllib.request.urlopen(req) as response:
            with open(dest, 'wb') as out:
                out.write(response.read())
        print(f"  完成: {dest}")
        return True
    except Exception as e:
        print(f"  失败: {e}")
        return False


def main():
    # 字体目录 - 放在 src/ui/resources/fonts/
    font_dir = Path(__file__).parent / "src" / "ui" / "resources" / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)

    print("MBD_CICDKits 字体下载器")
    print("=" * 50)
    print(f"目标目录: {font_dir}")
    print()

    # 字体下载列表 - 使用可靠的镜像源
    fonts = [
        ("Poppins-Regular", "https://raw.githubusercontent.com/googlefonts/poppins/main/fonts/ttf/Poppins-Regular.ttf"),
        ("Poppins-Bold", "https://raw.githubusercontent.com/googlefonts/poppins/main/fonts/ttf/Poppins-Bold.ttf"),
        ("Lora-Regular", "https://raw.githubusercontent.com/googlefonts/lora/main/fonts/ttf/Lora-Regular.ttf"),
        ("Lora-Bold", "https://raw.githubusercontent.com/googlefonts/lora/main/fonts/ttf/Lora-Bold.ttf"),
    ]

    # 备用方案 - 使用 googlefonts 官方
    backup_fonts = [
        ("Poppins-Regular", "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf"),
        ("Poppins-Bold", "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"),
        ("Lora-Regular", "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Regular.ttf"),
        ("Lora-Bold", "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Bold.ttf"),
    ]

    success = 0
    total = len(fonts)

    for i, (name, url) in enumerate(fonts):
        dest = font_dir / f"{name}.ttf"

        if dest.exists():
            print(f"[跳过] {name}.ttf 已存在")
            success += 1
            continue

        # 首先尝试主要 URL
        if download_file(url, dest):
            success += 1
            continue

        # 失败，尝试备用 URL
        if download_file(backup_fonts[i][1], dest):
            success += 1
            continue

        print()

    print("=" * 50)
    print(f"完成: {success}/{total} 个字体文件")

    if success == total:
        print("字体下载完成！现在可以运行应用了。")
    else:
        print("部分字体下载失败，应用将使用 fallback 字体。")


if __name__ == "__main__":
    main()
