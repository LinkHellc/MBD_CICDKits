"""单元测试：路径检测模块

测试 MATLAB 和 IAR 安装路径的自动检测功能。
"""

import logging
import platform
from pathlib import Path

import pytest

# 导入被测试模块
from utils.path_detector import (
    detect_matlab_installations,
    detect_iar_installations,
    auto_detect_paths,
    MATLAB_SEARCH_PATHS,
    IAR_SEARCH_PATHS,
)

logger = logging.getLogger(__name__)


class TestDetectMatlab:
    """测试 MATLAB 安装检测"""

    def test_detect_latest_version(self, tmp_path, monkeypatch):
        """测试选择最新版本"""
        # 创建模拟目录结构
        matlab_root = tmp_path / "MATLAB"
        matlab_root.mkdir()

        r2022a = matlab_root / "R2022a"
        r2022a.mkdir()
        (r2022a / "bin" / "win64").mkdir(parents=True)
        (r2022a / "bin" / "win64" / "MATLAB.exe").touch()

        r2023b = matlab_root / "R2023b"
        r2023b.mkdir()
        (r2023b / "bin" / "win64").mkdir(parents=True)
        (r2023b / "bin" / "win64" / "MATLAB.exe").touch()

        # 替换搜索路径
        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [matlab_root])
        # 临时设置为 Windows 平台
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_matlab_installations()
        assert result is not None
        assert result == r2023b  # 应该选择最新版本

    def test_detect_with_same_year_different_release(self, tmp_path, monkeypatch):
        """测试同年份不同版本选择（b > a）"""
        matlab_root = tmp_path / "MATLAB"
        matlab_root.mkdir()

        r2023a = matlab_root / "R2023a"
        r2023a.mkdir()
        (r2023a / "bin" / "win64").mkdir(parents=True)
        (r2023a / "bin" / "win64" / "MATLAB.exe").touch()

        r2023b = matlab_root / "R2023b"
        r2023b.mkdir()
        (r2023b / "bin" / "win64").mkdir(parents=True)
        (r2023b / "bin" / "win64" / "MATLAB.exe").touch()

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [matlab_root])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_matlab_installations()
        assert result == r2023b  # R2023b > R2023a

    def test_no_installation_found(self, tmp_path, monkeypatch):
        """测试未找到安装"""
        import utils.path_detector
        empty_dir = tmp_path / "Empty"
        empty_dir.mkdir()
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [empty_dir])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_matlab_installations()
        assert result is None

    def test_invalid_directory_name_ignored(self, tmp_path, monkeypatch):
        """测试忽略无效的目录名"""
        matlab_root = tmp_path / "MATLAB"
        matlab_root.mkdir()

        # 有效安装
        r2023a = matlab_root / "R2023a"
        r2023a.mkdir()
        (r2023a / "bin" / "win64").mkdir(parents=True)
        (r2023a / "bin" / "win64" / "MATLAB.exe").touch()

        # 无效目录名（应被忽略）
        invalid_dir = matlab_root / "InvalidFolder"
        invalid_dir.mkdir()

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [matlab_root])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_matlab_installations()
        assert result == r2023a

    def test_missing_exe_file_ignored(self, tmp_path, monkeypatch):
        """测试缺少可执行文件的目录被忽略"""
        matlab_root = tmp_path / "MATLAB"
        matlab_root.mkdir()

        # 目录名正确但缺少 exe 文件
        r2023a = matlab_root / "R2023a"
        r2023a.mkdir()
        # 不创建 MATLAB.exe

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [matlab_root])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_matlab_installations()
        assert result is None

    def test_non_windows_platform(self, monkeypatch):
        """测试非 Windows 平台返回 None"""
        import utils.path_detector
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Linux")

        result = detect_matlab_installations()
        assert result is None


class TestDetectIAR:
    """测试 IAR 安装检测"""

    def test_detect_iar_with_version(self, tmp_path, monkeypatch):
        """测试 IAR 检测"""
        iar_root = tmp_path / "IAR Systems"
        iar_root.mkdir()

        ew9_2 = iar_root / "Embedded Workbench 9.2"
        ew9_2.mkdir()
        (ew9_2 / "iarbuild.exe").touch()

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [iar_root])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_iar_installations()
        assert result is not None
        assert result == ew9_2

    def test_detect_latest_iar_version(self, tmp_path, monkeypatch):
        """测试选择最新 IAR 版本"""
        iar_root = tmp_path / "IAR Systems"
        iar_root.mkdir()

        ew9_2 = iar_root / "Embedded Workbench 9.2"
        ew9_2.mkdir()
        (ew9_2 / "iarbuild.exe").touch()

        ew9_3 = iar_root / "Embedded Workbench 9.3"
        ew9_3.mkdir()
        (ew9_3 / "iarbuild.exe").touch()

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [iar_root])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_iar_installations()
        assert result == ew9_3  # 应该选择 9.3

    def test_no_iar_installation_found(self, tmp_path, monkeypatch):
        """测试未找到 IAR 安装"""
        import utils.path_detector
        empty_dir = tmp_path / "Empty"
        empty_dir.mkdir()
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [empty_dir])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = detect_iar_installations()
        assert result is None

    def test_non_windows_platform_iar(self, monkeypatch):
        """测试非 Windows 平台 IAR 检测返回 None"""
        import utils.path_detector
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Linux")

        result = detect_iar_installations()
        assert result is None


class TestAutoDetectPaths:
    """测试综合路径检测"""

    def test_auto_detect_returns_dict(self, tmp_path, monkeypatch):
        """测试返回值是包含两个键的字典"""
        import utils.path_detector
        empty_dir = tmp_path / "Empty"
        empty_dir.mkdir()
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [empty_dir])
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [empty_dir])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = auto_detect_paths()

        assert isinstance(result, dict)
        assert "matlab" in result
        assert "iar" in result

    def test_auto_detect_with_both_found(self, tmp_path, monkeypatch):
        """测试同时检测到 MATLAB 和 IAR"""
        matlab_root = tmp_path / "MATLAB"
        matlab_root.mkdir()
        r2023a = matlab_root / "R2023a"
        r2023a.mkdir()
        (r2023a / "bin" / "win64").mkdir(parents=True)
        (r2023a / "bin" / "win64" / "MATLAB.exe").touch()

        iar_root = tmp_path / "IAR Systems"
        iar_root.mkdir()
        ew9_2 = iar_root / "Embedded Workbench 9.2"
        ew9_2.mkdir()
        (ew9_2 / "iarbuild.exe").touch()

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [matlab_root])
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [iar_root])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = auto_detect_paths()

        assert result["matlab"] is not None
        assert result["iar"] is not None
        assert result["matlab"] == r2023a
        assert result["iar"] == ew9_2

    def test_auto_detect_with_none_found(self, tmp_path, monkeypatch):
        """测试两者都未检测到"""
        import utils.path_detector
        empty_dir = tmp_path / "Empty"
        empty_dir.mkdir()
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [empty_dir])
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [empty_dir])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        result = auto_detect_paths()

        assert result["matlab"] is None
        assert result["iar"] is None


class TestErrorHandling:
    """测试错误处理"""

    def test_permission_error_handling(self, tmp_path, monkeypatch, caplog):
        """测试权限不足时的优雅处理"""
        import utils.path_detector

        # 创建一个存在的目录（但模拟权限错误）
        matlab_root = tmp_path / "MATLAB"
        matlab_root.mkdir()

        # 使用一个不存在的路径来触发异常
        nonexistent = tmp_path / "Nonexistent" / "Deep" / "Path"
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [nonexistent])
        monkeypatch.setattr(utils.path_detector.platform, "system", lambda: "Windows")

        # 应该返回 None 而不是抛出异常
        result = detect_matlab_installations()
        assert result is None
