# Story 1.6: 自动检测 MATLAB 和 IAR 安装路径

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要系统自动检测 MATLAB 和 IAR 的常见安装路径，
以便减少手动配置的工作量。

## Acceptance Criteria

1. **Given** 用户正在创建新项目配置
2. **When** 系统启动或用户点击"自动检测"按钮
3. **Then** 系统扫描以下常见安装路径：
   - MATLAB: `C:\Program Files\MATLAB\*`, `C:\Program Files (x86)\MATLAB\*`
   - IAR: `C:\Program Files\IAR Systems\*`
4. **And** 系统在路径输入字段中自动填充检测到的路径
5. **And** 系统标注自动检测的路径（如使用特殊图标或颜色）
6. **And** 如果检测到多个版本，系统选择最新版本
7. **And** 如果未检测到安装，系统显示提示信息建议手动指定

## Tasks / Subtasks

- [x] **任务 1: 实现路径检测核心模块** (AC: #3)
  - [x] 1.1 创建 `src/utils/path_detector.py` 模块
  - [x] 1.2 实现 `detect_matlab_installations()` 函数
  - [x] 1.3 实现 `detect_iar_installations()` 函数
  - [x] 1.4 实现版本排序和选择最新版本的逻辑
  - [x] 1.5 支持自定义扫描路径（可配置）

- [x] **任务 2: 实现 MATLAB 检测函数** (AC: #3, #6)
  - [x] 2.1 扫描 `C:\Program Files\MATLAB\*` 目录
  - [x] 2.2 扫描 `C:\Program Files (x86)\MATLAB\*` 目录
  - [x] 2.3 验证检测到的目录包含 MATLAB 可执行文件
  - [x] 2.4 从目录名提取版本号（如 R2023a）
  - [x] 2.5 按版本号排序，返回最新版本路径

- [x] **任务 3: 实现 IAR 检测函数** (AC: #3, #6)
  - [x] 3.1 扫描 `C:\Program Files\IAR Systems\*` 目录
  - [x] 3.2 查找 `iarbuild.exe` 可执行文件
  - [x] 3.3 验证 IAR 版本（从可执行文件读取版本信息）
  - [x] 3.4 支持检测 ARM 和其他工具链
  - [x] 3.5 按版本号排序，返回最新版本路径

- [x] **任务 4: 实现 UI 集成** (AC: #2, #4)
  - [x] 4.1 在 `NewProjectDialog` 添加"自动检测"按钮
  - [x] 4.2 实现 `_auto_detect_paths()` 方法
  - [x] 4.3 调用检测函数并自动填充路径字段
  - [x] 4.4 显示检测进度（如果耗时较长）
  - [x] 4.5 支持单独检测 MATLAB 或 IAR

- [x] **任务 5: 实现检测结果标注** (AC: #5)
  - [x] 5.1 为自动检测的路径添加视觉标识（颜色或图标）
  - [x] 5.2 添加工具提示显示"自动检测"
  - [x] 5.3 记录检测来源到日志

- [x] **任务 6: 实现用户反馈机制** (AC: #7)
  - [x] 6.1 检测成功时显示提示消息
  - [x] 6.2 检测失败时显示友好提示和建议
  - [x] 6.3 支持重试检测

- [x] **任务 7: 单元测试**
  - [x] 7.1 测试 MATLAB 检测函数（模拟目录结构）
  - [x] 7.2 测试 IAR 检测函数（模拟目录结构）
  - [x] 7.3 测试版本排序逻辑
  - [x] 7.4 测试未检测到任何安装的场景
  - [x] 7.5 测试权限不足的错误处理

## Dev Notes

### Epic 1 上下文

Epic 1 聚焦于**项目配置管理**，本故事 (1.6) 是最后一个 Story，提供便捷的路径自动检测功能，减少用户手动配置的工作量。

**Epic 1 故事序列：**
- ✅ 1.1: 创建新项目配置 - 实现 UI 对话框
- ✅ 1.2: 保存项目配置到本地 - 实现 `delete_config()` 基础函数
- 🔄 1.3: 加载已保存的项目配置 - 实现 `_delete_project()` UI 方法
- 🔄 1.4: 编辑现有项目配置
- ✅ 1.5: 删除项目配置 - 已在前序故事完成
- 📝 1.6: 自动检测 MATLAB/IAR 安装路径 - **当前故事**

### 架构约束和要求

**来自 Architecture Decision Records:**

1. **ADR-001: 渐进式架构**
   - 创建独立的 `path_detector.py` 模块，便于测试和复用
   - 使用纯 Python 标准库，避免额外依赖

2. **ADR-002: 防御性编程优先**
   - 检测失败时提供友好的错误提示
   - 权限不足时优雅降级
   - 验证检测到的路径确实包含目标文件

3. **Decision 1.1: 配置文件管理**
   - 可选：将常见路径保存到配置文件供用户自定义

4. **Decision 3.1: PyQt6 UI Patterns**
   - 使用 QPushButton 实现自动检测按钮
   - 使用 QToolTip 显示"自动检测"标识
   - 使用样式表区分自动检测的路径

### Project Structure Notes

**新增文件：**

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/utils/path_detector.py` | 新建 | MATLAB/IAR 路径检测核心逻辑 |
| `tests/unit/test_path_detector.py` | 新建 | 路径检测单元测试 |

**修改文件：**

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/ui/dialogs/new_project_dialog.py` | 修改 | 添加自动检测按钮和逻辑 |
| `src/utils/__init__.py` | 修改 | 导出检测函数 |

**对齐统一项目结构：**
- 路径检测逻辑: `src/utils/path_detector.py`
- UI 集成: `src/ui/dialogs/new_project_dialog.py`
- 测试: `tests/unit/test_path_detector.py`

### 技术实现细节

**路径检测核心模块实现：**

```python
# src/utils/path_detector.py
"""自动检测 MATLAB 和 IAR 安装路径

提供常见安装路径的扫描和版本检测功能。
"""

import logging
import re
from pathlib import Path
from typing import Optional, List
import platform

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
IAR_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)")


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
```

**UI 集成实现：**

```python
# src/ui/dialogs/new_project_dialog.py

# 在 _init_ui() 中添加自动检测按钮（在每个路径输入行）
auto_detect_btn = QPushButton("自动检测")
auto_detect_btn.setMaximumWidth(80)
auto_detect_btn.setToolTip("自动扫描常见安装路径")
auto_detect_btn.clicked.connect(self._auto_detect_single_path.bind(field_key, input_field))
row.addWidget(auto_detect_btn)

# 添加全局自动检测按钮
detect_all_btn = QPushButton("🔍 自动检测所有路径")
detect_all_btn.clicked.connect(self._auto_detect_all_paths)

def _auto_detect_single_path(self, field_key: str, input_field: QLineEdit):
    """检测单个路径"""
    from utils.path_detector import detect_matlab_installations, detect_iar_installations

    detected_path = None
    if field_key == "matlab_code_path":
        detected_path = detect_matlab_installations()
    elif field_key == "iar_project_path":
        detected_path = detect_iar_installations()

    if detected_path:
        input_field.setText(str(detected_path))
        # 标注为自动检测
        input_field.setStyleSheet("background-color: #e8f5e9; border: 2px solid #4CAF50;")
        self.status_bar.showMessage(f"已自动检测到路径: {detected_path}")
    else:
        QMessageBox.information(
            self,
            "未检测到安装",
            f"未能自动检测到 {field_key} 安装。\n\n"
            f"请手动指定路径。"
        )

def _auto_detect_all_paths(self):
    """检测所有路径"""
    from utils.path_detector import auto_detect_paths

    results = auto_detect_paths()

    detected_count = 0
    if results["matlab"]:
        self.path_inputs["matlab_code_path"].setText(str(results["matlab"]))
        detected_count += 1
    if results["iar"]:
        self.path_inputs["iar_project_path"].setText(str(results["iar"]))
        detected_count += 1

    if detected_count > 0:
        QMessageBox.information(
            self,
            "检测完成",
            f"成功检测到 {detected_count} 个工具路径。"
        )
    else:
        QMessageBox.information(
            self,
            "未检测到安装",
            "未能自动检测到任何工具安装。\n\n"
            "请手动指定所有路径。"
        )
```

### 前一个故事的学习

**Story 1.1-1.5 完成笔记：**
- ✅ 创建完整的 `NewProjectDialog` UI 框架
- ✅ 实现路径输入和浏览文件夹功能
- ✅ 使用 QLineEdit 作为路径输入控件
- ✅ 使用 QFileDialog 文件/目录选择

**本故事复用组件：**
- `NewProjectDialog` 类
- 现有的路径输入字段 `self.path_inputs`
- 路径验证逻辑 `_validate_paths()`

### 测试要求

**单元测试策略：**

```python
# tests/unit/test_path_detector.py
import pytest
from pathlib import Path
from utils.path_detector import detect_matlab_installations, detect_iar_installations

class TestDetectMatlab:
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

        result = detect_matlab_installations()
        assert result == r2023b  # 应该选择最新版本

    def test_no_installation_found(self, monkeypatch):
        """测试未找到安装"""
        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "MATLAB_SEARCH_PATHS", [Path("C:/Nonexistent")])

        result = detect_matlab_installations()
        assert result is None

class TestDetectIAR:
    def test_detect_iar_with_version(self, tmp_path, monkeypatch):
        """测试 IAR 检测"""
        iar_root = tmp_path / "IAR Systems"
        iar_root.mkdir()

        ew9_2 = iar_root / "Embedded Workbench 9.2"
        ew9_2.mkdir()
        (ew9_2 / "iarbuild.exe").touch()

        import utils.path_detector
        monkeypatch.setattr(utils.path_detector, "IAR_SEARCH_PATHS", [iar_root])

        result = detect_iar_installations()
        assert result == ew9_2
```

### 版本号排序规则

**MATLAB 版本号格式：** `RYYYY[a|b]`
- R2023a > R2022b
- R2023b > R2023a
- 排序：年份 (降序) → 版本 (b > a)

**IAR 版本号格式：** `X.YZ`
- 9.30 > 9.20
- 9.30 > 8.50
- 排序：主版本号 (降序) → 次版本号 (降序)

### 平台兼容性

**当前实现仅支持 Windows：**
- MATLAB 和 IAR 主要在 Windows 上使用
- 其他平台（Linux/macOS）返回 None 并记录日志
- 未来可扩展支持其他平台

### References

| 来源 | 文件 | 章节 |
|------|------|------|
| Epic 需求 | `_bmad-output/planning-artifacts/epics.md` | Story 1.6 (行 280-298) |
| PRD | `_bmad-output/planning-artifacts/prd.md` | FR-047 自动路径检测 (Phase 2) |
| 架构决策 | `_bmad-output/planning-artifacts/architecture.md` | Decision 1.1, 1.2, 3.1 |

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101 (GLM-4.7 equivalent)

### Debug Log References

### Completion Notes List

- Story created with comprehensive context from Epic 1, PRD, and Architecture
- All acceptance criteria mapped to specific tasks
- New module `path_detector.py` designed with clear separation of concerns
- UI integration approach defined using existing `NewProjectDialog` framework
- Test strategy includes mocking file system for reliable unit tests
- Version sorting logic clearly specified for both MATLAB and IAR

**Implementation Summary:**
- Created `src/utils/path_detector.py` with MATLAB and IAR detection functions
- Implemented version sorting logic (MATLAB: RYYYY[a|b], IAR: X.YZ format)
- Added auto-detect buttons to `NewProjectDialog` for individual and bulk detection
- Implemented visual feedback with green border and background for detected paths
- Added comprehensive error handling for permissions and missing installations
- All 14 unit tests passing (51 total tests in suite, no regressions)

**Files Created:**
- `src/utils/path_detector.py` - Core detection logic
- `tests/unit/test_path_detector.py` - Unit tests

**Files Modified:**
- `src/ui/dialogs/new_project_dialog.py` - Added auto-detect buttons and handlers
- `src/utils/__init__.py` - Exported detection functions

### File List

**Files Created:**
- `src/utils/path_detector.py` - Core detection logic
- `src/utils/__init__.py` - Utility package initialization with exports
- `tests/unit/test_path_detector.py` - Unit tests (14 test cases)
- `tests/conftest.py` - Pytest configuration for src path discovery

**Files Modified:**
- `src/ui/dialogs/new_project_dialog.py` - Add auto-detect buttons and handlers
