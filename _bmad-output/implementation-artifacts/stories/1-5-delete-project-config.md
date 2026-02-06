# Story 1.5: 删除项目配置

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要删除不再需要的项目配置，
以便保持项目列表的整洁。

## Acceptance Criteria

1. **Given** 项目列表中存在至少一个项目配置
2. **When** 用户选择一个项目并点击"删除"按钮
3. **Then** 系统显示确认对话框要求用户确认删除操作
4. **When** 用户确认删除
5. **Then** 系统从文件系统删除对应的 TOML 文件
6. **And** 系统从项目列表中移除该项目
7. **And** 系统显示删除成功的提示

## Tasks / Subtasks

- [x] **任务 1: 实现删除核心函数** (AC: #5)
  - [x] 1.1 在 `core/config.py` 实现 `delete_config()` 函数
  - [x] 1.2 使用 `Path.unlink()` 删除 TOML 文件
  - [x] 1.3 处理文件不存在的场景
  - [x] 1.4 记录删除操作到日志

- [x] **任务 2: 实现删除 UI 功能** (AC: #1, #2)
  - [x] 2.1 在 `MainWindow` 添加"删除"按钮
  - [x] 2.2 实现 `_delete_project()` 方法
  - [x] 2.3 显示确认对话框（QMessageBox.question）
  - [x] 2.4 用户选择"取消"时中止操作

- [x] **任务 3: 实现列表更新和反馈** (AC: #4, #6, #7)
  - [x] 3.1 删除成功后刷新项目列表
  - [x] 3.2 清空当前项目显示（如果删除的是当前项目）
  - [x] 3.3 显示删除成功/失败的消息
  - [x] 3.4 记录删除操作到日志

- [x] **任务 4: 单元测试**
  - [x] 4.1 测试成功删除配置文件
  - [x] 4.2 测试删除不存在的配置返回 False
  - [x] 4.3 测试删除后文件确实被移除

## Dev Notes

### Epic 1 上下文

Epic 1 聚焦于**项目配置管理**，本故事 (1.5) 完成 CRUD 操作中的"删除"功能。

**Epic 1 故事序列：**
- ✅ 1.1: 创建新项目配置 - 实现 UI 对话框
- ✅ 1.2: 保存项目配置到本地 - 实现 `delete_config()` 基础函数
- 🔄 1.3: 加载已保存的项目配置 - 实现 `_delete_project()` UI 方法
- 🔄 1.4: 编辑现有项目配置
- 📝 1.5: 删除项目配置 - **当前故事**
- ⏸️ 1.6: 自动检测 MATLAB/IAR 安装路径

### 实现状态说明

**本故事已在 Story 1.2 和 1.3 中完成！**

- **Story 1.2** 时实现了 `delete_config()` 核心函数作为基础配置管理功能
- **Story 1.3** 时在 `main_window.py` 实现了 `_delete_project()` UI 方法
- 所有验收标准均已满足，代码已通过单元测试

### 架构约束和要求

**来自 Architecture Decision Records:**

1. **ADR-001: 渐进式架构**
   - 复用现有的项目列表 UI 组件
   - 使用 QMessageBox 实现确认对话框

2. **ADR-002: 防御性编程优先**
   - 删除前显示确认对话框，防止误操作
   - 删除不存在文件时返回 False 而非抛出异常

3. **Decision 1.1: 配置文件管理**
   - 配置目录: `%APPDATA%/MBD_CICDKits/projects/`
   - 文件格式: TOML

### Project Structure Notes

**相关文件：**

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/core/config.py` | 已修改 (Story 1.2) | 包含 `delete_config()` 函数 |
| `src/ui/main_window.py` | 已修改 (Story 1.3) | 包含 `_delete_project()` 方法 |
| `tests/unit/test_config.py` | 已添加 (Story 1.2) | 包含 `test_delete_config()` 测试 |

**对齐统一项目结构：**
- 配置删除逻辑: `src/core/config.py`
- UI 删除交互: `src/ui/main_window.py`
- 测试: `tests/unit/test_config.py`

### 技术实现细节

**删除核心函数实现（已在 Story 1.2 完成）：**

```python
# src/core/config.py (行 204-226)
def delete_config(filename: str) -> bool:
    """删除配置文件

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        bool: 删除是否成功
    """
    try:
        config_file = CONFIG_DIR / f"{filename}.toml"

        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            return False

        config_file.unlink()
        logger.info(f"配置已删除: {config_file}")
        return True

    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        return False
```

**删除 UI 方法实现（已在 Story 1.3 完成）：**

```python
# src/ui/main_window.py (行 294-318)
def _delete_project(self):
    """删除选中的项目"""
    current_data = self.project_combo.currentData()
    if current_data is None:
        QMessageBox.warning(self, "未选择项目", "请先选择要删除的项目。")
        return

    project_name = current_data
    reply = QMessageBox.question(
        self,
        "确认删除",
        f"确定要删除项目 '{project_name}' 吗？\n\n此操作无法撤销！",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
        from core.config import delete_config
        if delete_config(project_name):
            self._refresh_project_list()
            self._clear_display()
            self.status_bar.showMessage(f"已删除项目: {project_name}")
            logger.info(f"项目已删除: {project_name}")
        else:
            QMessageBox.warning(self, "删除失败", f"无法删除项目: {project_name}")
```

### 前一个故事的学习

**Story 1.1 完成笔记：**
- ✅ 创建 `MainWindow` 类
- ✅ 实现项目列表下拉框

**Story 1.2 完成笔记：**
- ✅ 实现 `delete_config()` 基础函数

**Story 1.3 完成笔记：**
- ✅ 实现 `_delete_project()` UI 方法
- ✅ 添加删除按钮到主窗口
- ✅ 实现确认对话框和反馈

**本故事复用组件：**
- `MainWindow` 类
- `delete_config()` 核心函数
- `QMessageBox` 确认对话框
- `_refresh_project_list()` 刷新列表

### 测试要求

**单元测试（已在 Story 1.2 完成）：**

```python
# tests/unit/test_config.py (行 178-210)
def test_delete_config():
    """测试删除配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建配置（包含所有必填字段）
            config = ProjectConfig(
                name="to_delete",
                simulink_path="C:\\Test",
                matlab_code_path="C:\\Test",
                a2l_path="C:\\Test",
                target_path="C:\\Test",
                iar_project_path="C:\\Test.eww"
            )
            save_config(config, "to_delete")

            # 验证存在
            config_file = Path(tmpdir) / "to_delete.toml"
            assert config_file.exists()

            # 删除
            assert delete_config("to_delete") is True
            assert not config_file.exists()

            # 删除不存在的配置
            assert delete_config("nonexistent") is False

        finally:
            core.config.CONFIG_DIR = original_dir
```

### References

| 来源 | 文件 | 章节 |
|------|------|------|
| Epic 需求 | `_bmad-output/planning-artifacts/epics.md` | Story 1.5 (行 262-278) |
| PRD | `_bmad-output/planning-artifacts/prd.md` | FR-004 删除项目配置 |
| 架构决策 | `_bmad-output/planning-artifacts/architecture.md` | Decision 1.1, 1.2, 3.1 |

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101 (GLM-4.7 equivalent)

### Completion Notes List

- Story created with comprehensive context from Epic 1, PRD, and existing code
- **发现：本故事已在 Story 1.2 和 1.3 中完成实现！**
- All acceptance criteria already met by existing code
- No implementation work required - story can be marked as done

**Implementation Status:**

**已完成功能（来自前序故事）：**

✅ **任务 1: 实现删除核心函数** (Story 1.2)
- `delete_config()` 函数位于 `src/core/config.py` 行 204-226
- 使用 `Path.unlink()` 删除 TOML 文件
- 文件不存在时返回 False
- 记录删除操作到日志

✅ **任务 2: 实现删除 UI 功能** (Story 1.3)
- 删除按钮位于 `src/ui/main_window.py` 行 82-84
- `_delete_project()` 方法位于行 294-318
- 使用 `QMessageBox.question()` 显示确认对话框
- 用户选择"取消"时中止操作

✅ **任务 3: 实现列表更新和反馈** (Story 1.3)
- 删除成功后调用 `_refresh_project_list()` 刷新列表
- 删除当前项目时调用 `_clear_display()` 清空显示
- 使用 `status_bar.showMessage()` 显示删除成功消息
- 使用 `logger.info()` 记录删除操作

✅ **任务 4: 单元测试** (Story 1.2)
- `test_delete_config()` 位于 `tests/unit/test_config.py` 行 178-210
- 测试成功删除场景
- 测试删除不存在的配置返回 False
- 测试删除后文件确实被移除

### File List

**Files Modified (in previous stories):**
- `src/core/config.py` - Added `delete_config()` function (Story 1.2)
- `src/ui/main_window.py` - Added `_delete_project()` method and delete button (Story 1.3)
- `tests/unit/test_config.py` - Added `test_delete_config()` test (Story 1.2)

**Files Referenced:**
- `src/core/models.py` - `ProjectConfig` dataclass
- `_bmad-output/implementation-artifacts/stories/1-2-save-project-config-locally.md` - `delete_config()` implementation
- `_bmad-output/implementation-artifacts/stories/1-3-load-saved-project-config.md` - `_delete_project()` implementation
