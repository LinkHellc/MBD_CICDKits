# Story 2.2: 加载自定义工作流配置

Status: in-progress

## Story

作为嵌入式开发工程师，
我想要加载自定义的工作流配置文件，
以便执行个性化的构建流程。

## Acceptance Criteria

**Given** 用户已创建自定义工作流配置 JSON 文件
**When** 用户选择"加载自定义工作流"选项
**Then** 系统显示文件选择对话框
**When** 用户选择一个 JSON 文件
**Then** 系统解析 JSON 文件内容
**And** 系统验证工作流配置的格式和结构
**And** 系统显示工作流的阶段列表
**And** 如果配置文件格式错误，系统显示具体的错误位置和建议

## Tasks / Subtasks

- [ ] 任务 1: 实现自定义工作流加载器 (AC: When - 选择自定义工作流, Then - 显示文件对话框)
  - [ ] 1.1 在 `src/core/config.py` 添加 `load_custom_workflow_config()` 函数
  - [ ] 1.2 使用 PyQt6 `QFileDialog` 显示文件选择对话框
  - [ ] 1.3 过滤显示 JSON 文件 (*.json)
  - [ ] 1.4 返回用户选择的文件路径

- [ ] 任务 2: 实现工作流配置解析器 (AC: When - 选择文件, Then - 解析 JSON 内容)
  - [ ] 2.1 在 `src/core/config.py` 添加 `parse_workflow_config()` 函数
  - [ ] 2.2 读取 JSON 文件内容
  - [ ] 2.3 解析 JSON 为 Python 字典
  - [ ] 2.4 转换为 `WorkflowConfig` 对象

- [ ] 任务 3: 实现工作流配置格式验证器 (AC: Then - 验证格式和结构)
  - [ ] 3.1 在 `src/core/validation.py` 创建 `validate_workflow_format()` 函数
  - [ ] 3.2 检查必需的字段是否存在（id, name, stages）
  - [ ] 3.3 检查 stages 列表结构是否正确
  - [ ] 3.4 检查每个 stage 的必需字段
  - [ ] 3.5 返回验证错误列表（空列表表示有效）

- [ ] 任务 4: 创建自定义工作流配置数据模型 (AC: Then - 解析 JSON 内容)
  - [ ] 4.1 确认 `src/core/models.py` 中已有 `WorkflowConfig` 和 `StageConfig` dataclass
  - [ ] 4.2 确保支持从 JSON 字典创建 `WorkflowConfig` 对象
  - [ ] 4.3 确保所有字段提供默认值

- [ ] 任务 5: 创建错误提示对话框 (AC: And - 显示具体错误位置)
  - [ ] 5.1 创建 `src/ui/dialogs/config_error_dialog.py`
  - [ ] 5.2 使用 PyQt6 `QDialog` 作为基类
  - [ ] 5.3 显示文件解析错误或验证错误
  - [ ] 5.4 显示具体的错误位置和建议

- [ ] 任务 6: 在工作流选择对话框中添加加载自定义配置按钮 (AC: When - 选择选项)
  - [ ] 6.1 在 `workflow_select_dialog.py` 添加"加载自定义配置"按钮
  - [ ] 6.2 点击按钮时调用 `load_custom_workflow_config()`
  - [ ] 6.3 解析并验证配置
  - [ ] 6.4 如果成功，显示自定义配置的阶段列表
  - [ ] 6.5 如果失败，显示错误对话框

- [ ] 任务 7: 保存加载的自定义工作流配置 (AC: Then - 显示阶段列表)
  - [ ] 7.1 将自定义配置保存到项目配置中
  - [ ] 7.2 更新 ProjectConfig 的 workflow_id 和 workflow_name
  - [ ] 7.3 标记为自定义配置（非预定义模板）

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-001（渐进式架构）**：MVP 使用函数式模块，PyQt6 类仅用于 UI 层
- **ADR-004（混合架构模式）**：UI 层用 PyQt6 类，业务逻辑用函数，数据模型用 dataclass
- **Decision 1.3（配置验证）**：手动验证 MVP，返回错误列表，友好的错误消息
- **Decision 3.1（PyQt6 线程）**：信号连接使用 `QueuedConnection`（跨线程时）

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 数据模型：使用 `dataclass`，所有字段提供默认值 `field(default=...)`
2. ⭐⭐⭐⭐⭐ 路径处理：使用 `pathlib.Path` 而非字符串
3. ⭐⭐⭐⭐ 配置验证：手动验证，返回错误列表，空列表表示有效
4. ⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/core/validation.py` | 新建 | 验证逻辑模块 |
| `src/core/models.py` | 修改 | 添加 ValidationResult dataclass |
| `src/ui/dialogs/validation_result_dialog.py` | 新建 | 验证结果显示对话框 |
| `src/ui/main_window.py` | 修改 | 集成验证按钮和逻辑 |

**确保符合项目结构**：
```
src/
├── ui/                          # PyQt6 类
│   ├── main_window.py           # 主窗口（需修改）
│   └── dialogs/
│       ├── workflow_select_dialog.py  # 已存在
│       └── validation_result_dialog.py  # 新建
├── core/                        # 业务逻辑（函数）
│   ├── config.py                # 配置管理（已存在）
│   ├── models.py                # 数据模型（需修改）
│   └── validation.py            # 验证逻辑（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| PyQt6 | 最新稳定版 | UI 框架 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| pathlib | 内置 | 路径处理 |
| logging | 内置 | 日志记录 |

### 测试标准

**单元测试要求**：
- 测试阶段依赖关系验证器（有效/无效依赖）
- 测试必需参数验证器（参数存在/缺失）
- 测试路径存在性验证器（路径存在/不存在）
- 测试统一验证入口函数
- 测试 ValidationResult dataclass

**集成测试要求**：
- 测试验证功能与主窗口的集成
- 测试验证结果对话框的显示

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理已完成）
- ✅ Story 2.1: 选择预定义工作流模板（工作流配置数据模型已创建）

**后续故事**：
- Story 2.3: 加载自定义工作流配置
- Story 2.4: 启动自动化构建流程

### 数据流设计

```
用户点击"加载自定义工作流"按钮
    │
    ▼
调用 load_custom_workflow_config()
    │
    ▼
显示文件选择对话框 (QFileDialog)
    │
    ├─→ 过滤: *.json
    └─→ 用户选择文件
    │
    ▼
读取并解析 JSON 文件
    │
    ├─→ 解析成功 → parse_workflow_config()
    └─→ 解析失败 → 显示错误对话框
    │
    ▼
验证工作流格式 (validate_workflow_format)
    │
    ├─→ 验证成功 → 创建 WorkflowConfig 对象
    └─→ 验证失败 → 显示错误对话框（具体错误位置）
    │
    ▼
显示工作流阶段列表
    │
    └─→ 更新工作流选择对话框
    │
    ▼
保存到项目配置
    │
    └─→ 更新 ProjectConfig.workflow_id/name
```

### 自定义工作流配置格式

**JSON 结构示例**：

```json
{
  "id": "my_custom_workflow",
  "name": "我的自定义工作流",
  "description": "自定义的构建流程",
  "estimated_time": 12,
  "stages": [
    {
      "name": "matlab_gen",
      "enabled": true,
      "timeout": 1800
    },
    {
      "name": "file_process",
      "enabled": true,
      "timeout": 300
    },
    {
      "name": "iar_compile",
      "enabled": true,
      "timeout": 1200
    },
    {
      "name": "a2l_process",
      "enabled": false
    },
    {
      "name": "package",
      "enabled": true,
      "timeout": 60
    }
  ]
}
```

**验证规则**：

```python
# 必需字段
REQUIRED_FIELDS = ["id", "name", "stages"]

# 每个阶段必需的字段
STAGE_REQUIRED_FIELDS = ["name", "enabled"]

# 可选的字段（提供默认值）
STAGE_OPTIONAL_FIELDS = {
    "timeout": 300  # 默认5分钟
}

# 有效的阶段名称
VALID_STAGE_NAMES = [
    "matlab_gen",
    "file_process",
    "iar_compile",
    "a2l_process",
    "package"
]
```

### 项目结构说明

**已检测到的结构**：
- Epic 1 已完成，项目配置管理功能已实现
- Story 2.1 已完成，工作流配置数据模型已创建
- 主窗口 (`main_window.py`) 已有基础 UI 框架
- 配置管理 (`config.py`) 已有基础功能
- 工作流选择对话框 (`workflow_select_dialog.py`) 已创建

**本故事需要扩展**：
- 在 `models.py` 中添加 ValidationResult dataclass
- 新建 `validation.py` 模块实现验证逻辑
- 新建验证结果显示对话框
- 在主窗口中集成验证功能

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-007](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 1.3](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-001](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-004](../planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used

glm-4.7 (Claude Code Agent)

### Debug Log References

- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Story File: `_bmad-output/implementation-artifacts/2-2-validate-workflow-config-effectiveness.md`
- Epics Source: `_bmad-output/planning-artifacts/epics.md`
- Architecture Source: `_bmad-output/planning-artifacts/architecture.md`

### Completion Notes List

- ✅ Story 2.2 implementation 文件已创建（加载自定义工作流配置）
- ✅ 所有 tasks/subtasks 已定义（7个任务，共23个子任务）
- ✅ 架构决策已应用
- ✅ 项目结构已对齐
- ✅ 强制执行规则已包含

### File List

**创建的文件**：
1. `_bmad-output/implementation-artifacts/stories/2-2-validate-workflow-config-effectiveness.md` - Story implementation 文件

**待创建的文件**（执行过程中）：
1. `src/ui/dialogs/config_error_dialog.py` - 配置错误提示对话框
2. `tests/unit/test_load_custom_workflow.py` - 自定义工作流加载测试
3. `tests/unit/test_parse_workflow_config.py` - 工作流配置解析测试
4. `tests/unit/test_validate_workflow_format.py` - 工作流格式验证测试
5. `tests/unit/test_config_error_dialog.py` - 错误对话框测试

**待修改的文件**（执行过程中）：
1. `src/core/config.py` - 添加加载自定义工作流函数
2. `src/core/validation.py` - 新建，添加工作流格式验证函数
3. `src/ui/dialogs/workflow_select_dialog.py` - 添加加载自定义配置按钮
4. `src/core/models.py` - 确认支持自定义配置（如有需要）
