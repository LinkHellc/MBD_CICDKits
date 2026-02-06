"""自动检测 MATLAB 和 IAR 安装路径

提供常见安装路径的扫描和版本检测功能。
"""

import logging
import platform
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Windows 常见安装路径
MATLAB_SEARCH_PATHS = [
    Path("C:/Program Files/MATLAB"),
    Path("C:/Program Files (x86)/MATLAB"),
]

IAR_SEARCH_PATHS = [
    Path("C:/Program Files/IAR Systems"),
]

# MATLAB 版本号正则（如 R2023a, R2022b）
MATLAB_VERSION_PATTERN = re.compile(r"^R(\d{4})([ab])$")

# IAR 版本号正则（如 9.30, 9.20）
IAR_VERSION_PATTERN = re.compile(r"(\d+)\.(\d+)")


def detect_matlab_installations() -> Optional[Path]:
    """检测 MATLAB 安装路径，返回最新版本

    扫描常见安装路径，查找所有 MATLAB 安装，
    返回版本号最高的安装路径。

    Returns:
        最新版本的 MATLAB 安装路径，未找到返回 None

    Examples:
        >>> detect_matlab_installations()
        WindowsPath('C:/Program Files/MATLAB/R2023a')
    """
    if platform.system() != "Windows":
        logger.warning("MATLAB 检测仅支持 Windows")
        return None

    installations = []

    for search_path in MATLAB_SEARCH_PATHS:
        if not search_path.exists():
            continue

        try:
            for item in search_path.iterdir():
                if not item.is_dir():
                    continue

                # 检查目录名是否匹配版本模式
                dirname = item.name
                match = MATLAB_VERSION_PATTERN.match(dirname)
                if not match:
                    continue

                # 验证包含 MATLAB 可执行文件
                matlab_exe = item / "bin" / "win64" / "MATLAB.exe"
                if not matlab_exe.exists():
                    continue

                # 提取版本号用于排序
                year = int(match.group(1))
                release = match.group(2)  # 'a' or 'b'
                release_num = 0 if release == 'a' else 1

                installations.append({
                    "path": item,
                    "year": year,
                    "release": release_num,
                    "version_str": dirname
                })
        except PermissionError:
            logger.warning(f"权限不足，无法访问 {search_path}")
            continue
        except Exception as e:
            logger.warning(f"扫描 {search_path} 时出错: {e}")
            continue

    if not installations:
        logger.info("未检测到 MATLAB 安装")
        return None

    # 按年份和版本排序，返回最新的
    latest = max(installations, key=lambda x: (x["year"], x["release"]))
    logger.info(f"检测到 MATLAB {latest['version_str']}: {latest['path']}")
    return latest["path"]


def detect_iar_installations() -> Optional[Path]:
    """检测 IAR 安装路径，返回最新版本

    扫描常见安装路径，查找 IAR Embedded Workbench 安装，
    返回版本号最高的安装路径。

    Returns:
        最新版本的 IAR 安装路径，未找到返回 None

    Examples:
        >>> detect_iar_installations()
        WindowsPath('C:/Program Files/IAR Systems/Embedded Workbench 9.3')
    """
    if platform.system() != "Windows":
        logger.warning("IAR 检测仅支持 Windows")
        return None

    installations = []

    for search_path in IAR_SEARCH_PATHS:
        if not search_path.exists():
            continue

        try:
            # 递归搜索包含 iarbuild.exe 的目录
            for root in search_path.rglob("iarbuild.exe"):
                root_path = root.parent

                # 尝试从目录名提取版本号
                dirname = root_path.name
                match = IAR_VERSION_PATTERN.search(dirname)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))

                    installations.append({
                        "path": root_path,
                        "major": major,
                        "minor": minor,
                        "version_str": f"{major}.{minor}"
                    })
        except PermissionError:
            logger.warning(f"权限不足，无法访问 {search_path}")
            continue
        except Exception as e:
            logger.warning(f"扫描 {search_path} 时出错: {e}")
            continue

    if not installations:
        logger.info("未检测到 IAR 安装")
        return None

    # 按版本号排序，返回最新的
    latest = max(installations, key=lambda x: (x["major"], x["minor"]))
    logger.info(f"检测到 IAR {latest['version_str']}: {latest['path']}")
    return latest["path"]


def auto_detect_paths() -> dict[str, Optional[Path]]:
    """自动检测所有工具路径

    Returns:
        包含检测结果的字典:
        {
            "matlab": Path or None,
            "iar": Path or None
        }
    """
    return {
        "matlab": detect_matlab_installations(),
        "iar": detect_iar_installations(),
    }
