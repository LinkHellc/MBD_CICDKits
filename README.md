# MBD_CICDKits - 嵌入式开发CI/CD自动化工具链

> 使用BMAD方法（Breakthrough Method of Agile AI Driven Development）开发的嵌入式项目构建自动化工具

## 项目概述

MBD_CICDKits是一个为嵌入式开发（MATLAB/Simulink、IAR）提供自动化CI/CD流程的工具，支持从代码生成到最终打包的全流程。

## 功能特性

- ✅ 项目配置管理（创建、保存、加载、编辑、删除）
- ✅ 工作流配置（预定义模板、自定义配置）
- ✅ 工作流验证（格式验证、依赖验证、参数验证、路径验证）
- ✅ 自动化构建流程（MATLAB代码生成 → 文件处理 → IAR编译 → A2L处理 → 打包）

## 开发方法

本项目使用**BMAD方法**（Agile AI Driven Development）进行开发：

- **Phase 1: Analysis** - 分析阶段（可选）
- **Phase 2: Planning** - 规划阶段（PRD、Architecture）
- **Phase 3: Solutioning** - 解决方案阶段（Epic/Story分解）
- **Phase 4: Implementation** - 实现阶段（敏捷开发）

## 当前进度

- **Epic 1**: 项目配置管理 - ✅ 100%完成（6个故事）
- **Epic 2**: 工作流管理 - 🔄 12.5%（2/16个故事）
  - Story 2.1: 选择预定义工作流模板 - ✅ 已完成
  - Story 2.2: 加载自定义工作流配置 - ✅ 已完成
  - Story 2.3: 验证工作流配置有效性 - 🔄 开发中...

## 技术栈

- **语言**: Python 3.10+
- **UI框架**: PyQt6
- **数据模型**: dataclass (Python 3.7+)
- **构建工具**: MATLAB Compiler, IAR Compiler
- **测试框架**: pytest

## 项目结构

```
181_CICDRedo/
├── src/                      # 源代码
│   ├── ui/                 # PyQt6 UI层
│   ├── core/               # 业务逻辑层（函数）
│   └── models.py           # 数据模型（dataclass）
├── tests/                   # 测试代码
│   └── unit/              # 单元测试
├── _bmad/                   # BMAD配置和输出
│   ├── bmm/                # BMAD方法配置
│   └── _bmad-output/       # BMAD输出文档
└── configs/                 # 配置模板
```

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/LinkHellc/181_CICDRedo.git

# 进入项目目录
cd 181_CICDRedo

# 安装依赖（如果有requirements.txt）
pip install -r requirements.txt

# 运行测试
pytest tests/

# 启动应用
python main.py
```

## BMAD开发流程

本项目使用BMAD方法进行AI驱动开发：

1. **创建Story**: PM代理从Epic创建Story implementation文件
2. **开发Story**: DEV代理实现Story中的tasks/subtasks
3. **代码审查**: DEV代理进行code review
4. **自动通知**: 每个Story完成后发送飞书通知
5. **自动推送**: 每个Story完成后自动推送到GitHub

## 许可证

MIT License

## 联系方式

- 项目仓库: https://github.com/LinkHellc/181_CICDRedo
- BMAD方法: https://github.com/LinkHellc/openclaw-bmad-method

---

**开发日期**: 2026年2月8日
**当前版本**: v0.1.0-alpha
