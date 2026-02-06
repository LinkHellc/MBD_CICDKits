# Story 1.2: 保存项目配置到本地

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要保存项目配置到本地文件系统，
以便下次使用时无需重新输入所有路径。

## Acceptance Criteria

1. **Given** 用户已填写完整的项目配置信息
   **When** 用户点击"保存"按钮
   **Then** 系统将配置保存为 TOML 格式文件到 `%APPDATA%/MBD_CICDKits/projects/` 目录

2. **And** 文件名使用用户输入的项目名称

3. **And** 系统显示保存成功提示

4. **And** 如果保存目录不存在，系统自动创建目录

5. **And** 如果文件已存在，系统提示用户是否覆盖

## Tasks / Subtasks

- [x] **Task 1: 完善配置保存的用户体验** (AC: #2, #3)
  - [x] Subtask 1.1: 添加项目名称输入字段（如果Story 1.1未包含）
  - [x] Subtask 1.2: 实现文件名清理逻辑（使用 `sanitize_filename()`）
  - [x] Subtask 1.3: 实现保存成功通知（QMessageBox.information）
  - [x] Subtask 1.4: 记录保存操作到日志

- [x] **Task 2: 实现配置目录自动创建** (AC: #4)
  - [x] Subtask 2.1: 确认 `save_config()` 中目录创建逻辑
  - [x] Subtask 2.2: 测试目录不存在时的创建行为

- [x] **Task 3: 实现文件覆盖检测和提示** (AC: #5)
  - [x] Subtask 3.1: 在保存前检查配置文件是否存在
  - [x] Subtask 3.2: 实现覆盖确认对话框（QMessageBox.question）
  - [x] Subtask 3.3: 处理用户选择（是/否/取消）

- [x] **Task 4: 增强配置保存函数** (Architecture Decision 1.1)
  - [x] Subtask 4.1: 确保 `save_config()` 支持覆盖模式
  - [x] Subtask 4.2: 添加保存前验证（调用 `ProjectConfig.validate_required_fields()`）
  - [x] Subtask 4.3: 增强错误处理和用户友好的错误消息

- [x] **Task 5: 完善配置数据模型** (Architecture Decision 1.2)
  - [x] Subtask 5.1: 确保 `ProjectConfig` 包含 `name` 字段
  - [x] Subtask 5.2: 添加 `created_at` 和 `modified_at` 时间戳
  - [x] Subtask 5.3: 实现 `to_dict()` 方法用于序列化

- [x] **Task 6: 单元测试**
  - [x] Subtask 6.1: 测试保存到不存在的目录
  - [x] Subtask 6.2: 测试覆盖已存在的配置文件
  - [x] Subtask 6.3: 测试文件名清理逻辑
  - [x] Subtask 6.4: 测试时间戳生成

## Dev Notes

### 前一故事（Story 1.1）的关键经验

**Story 1.1 Review 发现的问题（必须避免）**：

1. ❌ **CRITICAL**: 硬编码Windows路径 - 必须使用 `get_config_dir()` 实现跨平台
2. ❌ **CRITICAL**: `from_dict()` 缺少异常处理 - 必须过滤无效字段
3. ❌ **HIGH**: 配置覆盖未检测 - 本Story的核心需求
4. ❌ **HIGH**: `load_config()` 缺少验证 - 加载后必须验证
5. ❌ **HIGH**: IAR工程应选择文件 - 非目录

**Story 1.1 已建立的代码模式（复用）**：

```python
# ✅ 已验证的模式 - 直接使用
# 1. 配置目录（跨平台）
def get_config_dir() -> Path:
    """获取跨平台配置目录"""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "MBD_CICDKits" / "configs"
    else:
        return Path.home() / ".config" / "mbd_cicdkits" / "configs"

# 2. 文件名清理
def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    # 移除 < > : " / \ | ? * 以及控制字符
    # 限制长度为50字符
    # 去除首尾空格

# 3. 配置覆盖检测（Story 1.1修复后已实现）
config_file = CONFIG_DIR / f"{filename}.toml"
if config_file.exists():
    reply = QMessageBox.question(...)
```

### 架构遵循要求（CRITICAL）

本项目采用 **渐进式架构** 和 **混合架构模式**（ADR-001, ADR-004）：

1. **配置格式决策**（Architecture Decision 1.1）：
   - ✅ TOML 用于用户项目配置（支持注释，可手动编辑）
   - ❌ 不使用 JSON（用于工作流配置，非项目配置）

2. **数据模型**（Architecture Decision 1.2）：
   - 使用 `dataclass` (Python 3.7+)
   - 所有字段提供默认值 `field(default=...)`
   - 使用 `field(default_factory=dict)` 避免可变默认值陷阱

3. **错误处理**（Architecture Decision 4.x）：
   - 使用统一的错误类（`utils/errors.py`）
   - 提供可操作的修复建议（`suggestions`）

### 项目结构说明

根据 Architecture 项目结构（Project Structure & Boundaries）：

```
src/
├── ui/
│   └── dialogs/
│       └── new_project_dialog.py    # ← Story 1.1 已创建，需增强
├── core/
│   ├── config.py                     # ← Story 1.1 已创建，需增强
│   └── models.py                     # ← Story 1.1 已创建，可能需增强
└── utils/
    ├── errors.py                     # ← 统一错误类
    └── path_utils.py                 # ← 路径工具函数
```

### 配置保存增强实现

**必须在 `src/core/config.py` 中增强**：

```python
from pathlib import Path
import sys
import logging
from datetime import datetime
import tomli_w  # 需要安装: pip install tomli-w
from typing import Optional

from core.models import ProjectConfig
from utils.errors import ConfigSaveError, ConfigValidationError

logger = logging.getLogger(__name__)

def get_config_dir() -> Path:
    """获取跨平台配置目录

    Returns:
        Path: 配置目录路径
    """
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "MBD_CICDKits" / "configs"
    else:
        return Path.home() / ".config" / "mbd_cicdkits" / "configs"

def save_config(
    config: ProjectConfig,
    filename: str,
    overwrite: bool = False
) -> bool:
    """保存项目配置到 TOML 文件

    Args:
        config: 项目配置对象
        filename: 文件名（不含扩展名）
        overwrite: 是否覆盖已存在的文件

    Returns:
        bool: 保存是否成功

    Raises:
        ConfigSaveError: 保存失败时抛出
    """
    try:
        # 获取配置目录
        config_dir = get_config_dir()

        # 确保配置目录存在（AC #4）
        config_dir.mkdir(parents=True, exist_ok=True)

        # 验证配置（Story 1.1修复建议）
        errors = config.validate_required_fields()
        if errors:
            raise ConfigValidationError(
                f"配置验证失败: {', '.join(errors)}",
                suggestions=["检查所有必填字段是否已填写"]
            )

        # 检查文件是否存在（AC #5）
        config_file = config_dir / f"{filename}.toml"
        if config_file.exists() and not overwrite:
            return False  # 通知UI层显示确认对话框

        # 更新时间戳
        config.modified_at = datetime.now().isoformat()
        if not config.created_at:
            config.created_at = config.modified_at

        # 转换为字典（排除 None 值）
        config_dict = config.to_dict()

        # 保存为 TOML
        with open(config_file, "wb") as f:
            tomli_w.dump(config_dict, f)

        logger.info(f"配置已保存: {filename}")
        return True

    except ConfigValidationError:
        raise
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        raise ConfigSaveError(str(e))

def config_exists(filename: str) -> bool:
    """检查配置文件是否存在

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        bool: 文件是否存在
    """
    config_file = get_config_dir() / f"{filename}.toml"
    return config_file.exists()
```

### ProjectConfig 增强实现

**必须在 `src/core/models.py` 中增强**：

```python
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class ProjectConfig:
    """项目配置数据模型

    使用 dataclass 实现轻量级数据容器。
    所有字段提供默认值，确保版本兼容性。
    """
    # 基本信息
    name: str = ""
    description: str = ""

    # 必需路径
    simulink_path: str = ""           # Simulink 工程路径
    matlab_code_path: str = ""        # MATLAB 代码路径
    a2l_path: str = ""                # A2L 文件路径
    target_path: str = ""             # 目标文件路径
    iar_project_path: str = ""        # IAR 工程路径

    # 可选字段（预留 Phase 2 扩展）
    custom_params: dict = field(default_factory=dict)
    created_at: str = ""              # 创建时间戳（ISO格式）
    modified_at: str = ""             # 修改时间戳（ISO格式）

    def validate_required_fields(self) -> list[str]:
        """验证必填字段

        Returns:
            错误列表，空列表表示验证通过
        """
        errors = []
        required_fields = [
            ("name", "项目名称"),
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
        ]

        for field_key, field_name in required_fields:
            value = getattr(self, field_key, "")
            if not value or not value.strip():
                errors.append(f"{field_name} 不能为空")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（排除 None 值）

        Returns:
            配置字典
        """
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and v != ""
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        """从字典创建配置对象（Story 1.1 修复：过滤无效字段）

        Args:
            data: 配置字典

        Returns:
            ProjectConfig 对象
        """
        # 获取合法字段名
        valid_fields = {f.name for f in fields(cls)}

        # 过滤无效字段
        filtered_data = {
            k: v for k, v in data.items()
            if k in valid_fields
        }

        return cls(**filtered_data)
```

### UI 实现增强（基于 Story 1.1）

**在 `src/ui/dialogs/new_project_dialog.py` 中增强**：

```python
def _save_config(self):
    """保存配置（增强版：包含覆盖检测和文件名清理）"""
    # 验证路径
    errors = self._validate_paths()
    if errors:
        QMessageBox.warning(
            self,
            "验证失败",
            "\n".join(errors)
        )
        return

    # 获取项目名称并清理文件名
    raw_name = self.name_input.text().strip() if hasattr(self, 'name_input') else \
               self.path_inputs["simulink_path"].text().split("\\")[-1]

    # 清理文件名（使用 sanitize_filename）
    from utils.path_utils import sanitize_filename
    filename = sanitize_filename(raw_name)

    if not filename:
        QMessageBox.warning(
            self,
            "无效的项目名称",
            "项目名称不能为空或仅包含非法字符。"
        )
        return

    # 创建配置对象
    config = ProjectConfig(
        name=filename,
        simulink_path=self.path_inputs["simulink_path"].text(),
        matlab_code_path=self.path_inputs["matlab_code_path"].text(),
        a2l_path=self.path_inputs["a2l_path"].text(),
        target_path=self.path_inputs["target_path"].text(),
        iar_project_path=self.path_inputs["iar_project_path"].text(),
    )

    # 检查配置是否已存在（AC #5）
    from core.config import config_exists, save_config

    if config_exists(filename):
        reply = QMessageBox.question(
            self,
            "配置已存在",
            f"配置文件 '{filename}' 已存在。\n是否覆盖？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return  # 用户选择不覆盖

    # 保存配置
    try:
        if save_config(config, filename, overwrite=True):
            QMessageBox.information(
                self,
                "保存成功",
                f"配置已保存: {filename}"
            )
            logger.info(f"配置已保存: {filename}")
            self.config_saved.emit(filename)
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "保存失败",
                "配置保存失败，请查看日志。"
            )

    except Exception as e:
        QMessageBox.critical(
            self,
            "保存失败",
            f"配置保存失败:\n{str(e)}"
        )
```

### 文件名清理工具函数

**在 `src/utils/path_utils.py` 中实现**：

```python
import re
from pathlib import Path

def sanitize_filename(name: str, max_length: int = 50) -> str:
    """清理文件名中的非法字符

    Args:
        name: 原始文件名
        max_length: 最大长度限制

    Returns:
        清理后的文件名
    """
    if not name:
        return ""

    # 移除 Windows 非法字符: < > : " / \ | ? *
    # 以及控制字符 (0-31)
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    cleaned = re.sub(illegal_chars, '_', name)

    # 去除首尾空格和点
    cleaned = cleaned.strip('. ')

    # 限制长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()

    # 如果清理后为空，返回默认名称
    if not cleaned:
        cleaned = "unnamed_project"

    return cleaned
```

### 错误处理增强

**使用统一的错误类（`utils/errors.py`）**：

```python
class ConfigError(Exception):
    """配置相关错误基类"""
    def __init__(self, message: str, suggestions: list[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

class ConfigSaveError(ConfigError):
    """配置保存失败"""
    def __init__(self, reason: str):
        super().__init__(
            f"无法保存配置: {reason}",
            suggestions=[
                "检查配置目录权限",
                "确保磁盘空间充足",
                "查看详细日志获取更多信息"
            ]
        )

class ConfigValidationError(ConfigError):
    """配置验证失败"""
    def __init__(self, field: str, reason: str):
        super().__init__(
            f"配置验证失败: {field}: {reason}",
            suggestions=[
                f"检查 {field} 是否正确填写",
                "确保所有必填字段已填写",
                "查看配置表单中的红色提示"
            ]
        )
```

### 测试标准

根据 Architecture 测试优先级建议和 Story 1.1 经验：

```python
# tests/unit/test_config_save.py
import pytest
import tempfile
from pathlib import Path
from core.models import ProjectConfig
from core.config import save_config, config_exists
from utils.path_utils import sanitize_filename

def test_save_to_nonexistent_directory():
    """测试保存到不存在的目录（AC #4）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 修改配置目录指向临时目录的子目录
        import core.config
        original_dir = core.config.get_config_dir
        core.config.get_config_dir = lambda: Path(tmpdir) / "subdir" / "configs"

        try:
            config = ProjectConfig(
                name="test_project",
                simulink_path="C:\\Projects\\Test",
                matlab_code_path="C:\\MATLAB\\code"
            )

            # 保存应该自动创建目录
            assert save_config(config, "test_project") is True
            assert config_exists("test_project") is True

        finally:
            core.config.get_config_dir = original_dir

def test_overwrite_existing_config():
    """测试覆盖已存在的配置（AC #5）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config
        original_dir = core.config.get_config_dir
        core.config.get_config_dir = lambda: Path(tmpdir)

        try:
            # 第一次保存
            config1 = ProjectConfig(
                name="test",
                simulink_path="C:\\Old",
                matlab_code_path="C:\\Old"
            )
            assert save_config(config1, "test") is True

            # 检查文件存在
            assert config_exists("test") is True

            # 第二次保存（覆盖）
            config2 = ProjectConfig(
                name="test",
                simulink_path="C:\\New",
                matlab_code_path="C:\\New"
            )
            assert save_config(config2, "test", overwrite=True) is True

            # 验证覆盖成功
            loaded = load_config("test")
            assert loaded.simulink_path == "C:\\New"

        finally:
            core.config.get_config_dir = original_dir

def test_sanitize_filename():
    """测试文件名清理逻辑"""
    # 非法字符被替换
    assert sanitize_filename("test<file>name") == "test_file_name"

    # 首尾空格和点被移除
    assert sanitize_filename("  .test.  ") == "test"

    # 长度限制
    long_name = "a" * 100
    assert len(sanitize_filename(long_name)) == 50

    # 空字符串返回默认值
    assert sanitize_filename("") == "unnamed_project"

    # 特殊字符
    assert sanitize_filename('test:file/name?') == "test_file_name_"

def test_timestamp_generation():
    """测试时间戳生成"""
    from datetime import datetime

    config = ProjectConfig(
        name="test",
        simulink_path="C:\\Test",
        matlab_code_path="C:\\Test"
    )

    # 初始创建应该有时间戳
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config
        original_dir = core.config.get_config_dir
        core.config.get_config_dir = lambda: Path(tmpdir)

        try:
            save_config(config, "test")

            # 验证时间戳格式（ISO 8601）
            assert config.created_at != ""
            assert config.modified_at != ""

            # 验证可以解析为datetime
            datetime.fromisoformat(config.created_at)
            datetime.fromisoformat(config.modified_at)

        finally:
            core.config.get_config_dir = original_dir
```

### 项目结构说明

**模块边界**（Architectural Boundaries）：

```
┌─────────────────────────────────────┐
│         UI Layer (PyQt6)            │
│  ┌────────────────────────────────┐ │
│  │ NewProjectDialog (QDialog)     │ │
│  │ - _save_config() [增强]        │ │
│  │   - 覆盖检测                    │ │
│  │   - 文件名清理                  │ │
│  │   - 成功/失败通知               │ │
│  └────────────┬───────────────────┘ │
└───────────────┼───────────────────────┘
                │
                │ (直接调用)
                ▼
┌─────────────────────────────────────┐
│       Core Layer (Functions)        │
│  ┌────────────────────────────────┐ │
│  | save_config() [增强]           │ │
│  | - 跨平台目录                    │ │
│  | - 自动创建目录                  │ │
│  | - 时间戳更新                    │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  | config_exists() [新增]         │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  | ProjectConfig [增强]           │ │
│  | - validate_required_fields()   │ │
│  | - to_dict()                    │ │
│  | - from_dict() [Story 1.1修复]  │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│         Utils Layer                 │
│  ┌────────────────────────────────┐ │
│  | sanitize_filename() [新增]     │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  | ConfigSaveError [增强]         │ │
│  | ConfigValidationError [新增]   │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 引用来源

| 来源 | 文件/章节 |
|------|----------|
| Epic 详情 | `_bmad-output/planning-artifacts/epics.md` - Story 1.2 |
| PRD 需求 | `_bmad-output/planning-artifacts/prd.md` - FR-002 |
| 架构决策 | `_bmad-output/planning-artifacts/architecture.md` - Decision 1.1, 1.2, 4.1 |
| 项目结构 | `_bmad-output/planning-artifacts/architecture.md` - Project Structure |
| 前一Story | `_bmad-output/implementation-artifacts/stories/1-1-create-new-project-config.md` |
| UX 规范 | `_bmad-output/planning-artifacts/ux-design-specification.md` - 配置保存体验 |

### 约束和注意事项

1. **复用 Story 1.1 代码** - 本Story建立在1.1基础上，主要是增强而非重写
2. **Story 1.1 CRITICAL问题** - 必须使用跨平台 `get_config_dir()`，避免硬编码Windows路径
3. **Story 1.1 HIGH问题** - 配置覆盖检测是本Story核心需求（AC #5）
4. **配置格式** - 必须使用 TOML，不支持 JSON（Architecture Decision 1.1）
5. **Python 版本** - Python 3.10+ 使用 `tomli`，Python 3.11+ 使用内置 `tomllib`
6. **文件命名规范** - 使用 `sanitize_filename()` 确保跨平台兼容性
7. **时间戳格式** - 使用 ISO 8601 格式（`datetime.now().isoformat()`）

## Dev Agent Record

### Agent Model Used

GLM-4.7 (Dev Story Implementation)

### Debug Log References

无 - 实现过程顺利，无需调试

### Implementation Plan

**实现策略**：
1. 创建测试文件（RED phase）- 定义预期行为
2. 实现 `utils/path_utils.py` - 文件名清理函数
3. 实现 `utils/errors.py` - 统一错误处理类
4. 增强 `core/config.py` - 添加 `config_exists()` 和 `overwrite` 参数
5. 增强 `core/models.py` - 更新 `to_dict()` 和 `validate_required_fields()`
6. 增强 `ui/dialogs/new_project_dialog.py` - 添加项目名称输入和成功通知
7. 运行测试验证（GREEN phase）

- `tests/unit/test_config_save.py` - Story 1.2 单元测试（13 个测试用例）

### Code Review Fixes (2026-02-04)

**代码审查发现并修复的问题：**

**HIGH 优先级修复：**
1. ✅ 修复 AC #1 路径错误：将配置目录从 `configs` 改为 `projects`（符合需求规范）
2. ✅ 修复平台检测：使用 `sys.platform == "win32"` 替代 `os.name == 'nt'`（符合架构规范）

**MEDIUM 优先级修复：**
3. ✅ 增强覆盖测试：添加内容验证，确保覆盖后文件内容正确更新
4. ✅ 添加文档注释：为项目名称自动提取逻辑添加详细文档说明

**LOW 优先级修复：**
5. ✅ 创建 `get_projects_dir()` 函数：提高代码语义清晰度
6. ✅ 添加 TOML 格式验证测试：确保生成的文件格式正确

**测试结果：**
- 所有 13 个单元测试通过（包括新增的 TOML 格式测试）
- AC #1 路径已修正为 `%APPDATA%/MBD_CICDKits/projects/`
- 代码架构符合 Dev Notes 规范

### File List

**新建的文件**：
- `src/utils/__init__.py` - utils 模块初始化
- `src/utils/path_utils.py` - 文件名清理工具函数
- `src/utils/errors.py` - 统一错误处理类
- `tests/__init__.py` - 测试包初始化
- `tests/unit/__init__.py` - 单元测试包初始化
- `tests/conftest.py` - pytest 配置（设置 PYTHONPATH）
- `tests/unit/test_config_save.py` - Story 1.2 单元测试（12 个测试用例）

**修改的文件**：
- `src/core/config.py` - 添加 `config_exists()` 函数，增强 `save_config()` 支持 `overwrite` 参数和时间戳更新
- `src/core/models.py` - 更新 `to_dict()` 排除空字符串，更新 `validate_required_fields()` 包含 `name` 字段
- `src/ui/dialogs/new_project_dialog.py` - 添加项目名称输入字段，从 utils 导入 `sanitize_filename`，添加保存成功通知

---
