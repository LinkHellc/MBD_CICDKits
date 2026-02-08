"""Unit tests for loading custom workflow configuration (Story 2.2)

This module tests the load_custom_workflow function in src/core/config.py
"""

import json
import logging
import tempfile
from pathlib import Path
import pytest

from core.config import load_custom_workflow
from core.models import WorkflowConfig, StageConfig

logger = logging.getLogger(__name__)


class TestLoadCustomWorkflow:
    """Test suite for load_custom_workflow function"""

    def test_load_valid_custom_workflow(self, tmp_path):
        """Test loading a valid custom workflow configuration

        AC: When - 用户选择一个 JSON 文件
        Then - 系统解析 JSON 文件内容
        """
        # 创建有效的自定义工作流配置
        workflow_data = {
            "id": "custom_test",
            "name": "测试工作流",
            "description": "这是一个测试工作流",
            "estimated_time": 15,
            "stages": [
                {
                    "id": "matlab_gen",
                    "name": "MATLAB代码生成",
                    "enabled": True,
                    "timeout": 1800,
                    "dependencies": []
                },
                {
                    "id": "file_process",
                    "name": "文件处理",
                    "enabled": True,
                    "timeout": 300,
                    "dependencies": ["matlab_gen"]
                },
                {
                    "id": "iar_compile",
                    "name": "IAR编译",
                    "enabled": True,
                    "timeout": 1200,
                    "dependencies": ["file_process"]
                },
                {
                    "id": "a2l_process",
                    "name": "A2L处理",
                    "enabled": False,
                    "timeout": 600,
                    "dependencies": ["iar_compile"]
                },
                {
                    "id": "package",
                    "name": "打包",
                    "enabled": True,
                    "timeout": 60,
                    "dependencies": ["iar_compile"]
                }
            ]
        }

        # 创建临时JSON文件
        workflow_file = tmp_path / "custom_workflow.json"
        with open(workflow_file, "w", encoding="utf-8") as f:
            json.dump(workflow_data, f, ensure_ascii=False, indent=2)

        # 加载工作流
        workflow, error_msg = load_custom_workflow(workflow_file)

        # 验证结果
        assert error_msg is None, f"加载失败: {error_msg}"
        assert workflow is not None
        assert workflow.id == "custom_test"
        assert workflow.name == "测试工作流"
        assert workflow.description == "这是一个测试工作流"
        assert workflow.estimated_time == 15

        # 验证阶段
        assert len(workflow.stages) == 5
        assert workflow.stages[0].name == "matlab_gen"
        assert workflow.stages[0].enabled == True
        assert workflow.stages[0].timeout == 1800

        assert workflow.stages[3].name == "a2l_process"
        assert workflow.stages[3].enabled == False

    def test_file_not_exists(self):
        """Test loading a non-existent file

        AC: Then - 如果配置文件格式错误，系统显示具体的错误位置和建议
        """
        non_existent = Path("/non/existent/path.json")
        workflow, error_msg = load_custom_workflow(non_existent)

        assert workflow is None
        assert error_msg is not None
        assert "不存在" in error_msg

    def test_invalid_json_format(self, tmp_path):
        """Test loading a file with invalid JSON format

        AC: Then - 如果配置文件格式错误，系统显示具体的错误位置和建议
        """
        # 创建格式错误的JSON文件
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "JSON格式错误" in error_msg

    def test_missing_required_fields(self, tmp_path):
        """Test loading a workflow with missing required fields

        AC: Then - 系统验证工作流配置的格式和结构
        """
        # 缺少必需字段 "name"
        incomplete_data = {
            "description": "缺少name",
            "stages": [
                {
                    "id": "matlab_gen",
                    "name": "MATLAB代码生成",
                    "enabled": True,
                    "dependencies": []
                }
            ]
        }

        incomplete_file = tmp_path / "incomplete.json"
        with open(incomplete_file, "w", encoding="utf-8") as f:
            json.dump(incomplete_data, f)

        workflow, error_msg = load_custom_workflow(incomplete_file)

        assert workflow is None
        assert error_msg is not None
        assert "缺少必需字段" in error_msg
        assert "name" in error_msg

    def test_empty_stages_list(self, tmp_path):
        """Test loading a workflow with empty stages list

        AC: Then - 系统验证工作流配置的格式和结构
        """
        empty_stages_data = {
            "id": "empty",
            "name": "空工作流",
            "description": "没有阶段",
            "stages": []
        }

        empty_file = tmp_path / "empty.json"
        with open(empty_file, "w", encoding="utf-8") as f:
            json.dump(empty_stages_data, f)

        workflow, error_msg = load_custom_workflow(empty_file)

        assert workflow is None
        assert error_msg is not None
        assert "stages 列表不能为空" in error_msg

    def test_stage_missing_required_fields(self, tmp_path):
        """Test loading a workflow with stages missing required fields

        AC: Then - 系统验证工作流配置的格式和结构
        """
        # 阶段缺少 "enabled" 字段
        invalid_stage_data = {
            "id": "invalid",
            "name": "无效工作流",
            "description": "阶段缺少字段",
            "stages": [
                {
                    "id": "matlab_gen",
                    "name": "MATLAB代码生成",
                    # 缺少 "enabled"
                    "dependencies": []
                }
            ]
        }

        invalid_file = tmp_path / "invalid_stage.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_stage_data, f)

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "缺少必需字段" in error_msg

    def test_circular_dependencies(self, tmp_path):
        """Test loading a workflow with circular dependencies

        AC: Then - 系统验证工作流配置的格式和结构
        """
        circular_data = {
            "id": "circular",
            "name": "循环依赖",
            "description": "测试循环依赖检测",
            "stages": [
                {
                    "id": "stage_a",
                    "name": "阶段A",
                    "enabled": True,
                    "dependencies": ["stage_c"]
                },
                {
                    "id": "stage_b",
                    "name": "阶段B",
                    "enabled": True,
                    "dependencies": ["stage_a"]
                },
                {
                    "id": "stage_c",
                    "name": "阶段C",
                    "enabled": True,
                    "dependencies": ["stage_b"]  # 循环: A->C->B->A
                }
            ]
        }

        circular_file = tmp_path / "circular.json"
        with open(circular_file, "w", encoding="utf-8") as f:
            json.dump(circular_data, f)

        workflow, error_msg = load_custom_workflow(circular_file)

        assert workflow is None
        assert error_msg is not None
        assert "循环依赖" in error_msg

    def test_non_existent_dependency(self, tmp_path):
        """Test loading a workflow with non-existent dependency

        AC: Then - 系统验证工作流配置的格式和结构
        """
        invalid_dep_data = {
            "id": "invalid_dep",
            "name": "无效依赖",
            "description": "测试不存在的依赖",
            "stages": [
                {
                    "id": "stage_a",
                    "name": "阶段A",
                    "enabled": True,
                    "dependencies": ["non_existent"]  # 不存在的阶段
                }
            ]
        }

        invalid_dep_file = tmp_path / "invalid_dep.json"
        with open(invalid_dep_file, "w", encoding="utf-8") as f:
            json.dump(invalid_dep_data, f)

        workflow, error_msg = load_custom_workflow(invalid_dep_file)

        assert workflow is None
        assert error_msg is not None
        assert "不存在" in error_msg

    def test_no_enabled_stages(self, tmp_path):
        """Test loading a workflow with all stages disabled

        AC: Then - 系统验证工作流配置的格式和结构
        """
        all_disabled_data = {
            "id": "all_disabled",
            "name": "全部禁用",
            "description": "所有阶段都被禁用",
            "stages": [
                {
                    "id": "stage_a",
                    "name": "阶段A",
                    "enabled": False,
                    "dependencies": []
                },
                {
                    "id": "stage_b",
                    "name": "阶段B",
                    "enabled": False,
                    "dependencies": []
                }
            ]
        }

        all_disabled_file = tmp_path / "all_disabled.json"
        with open(all_disabled_file, "w", encoding="utf-8") as f:
            json.dump(all_disabled_data, f)

        workflow, error_msg = load_custom_workflow(all_disabled_file)

        assert workflow is None
        assert error_msg is not None
        assert "至少需要启用一个阶段" in error_msg

    def test_default_values(self, tmp_path):
        """Test loading a workflow with minimal fields (using defaults)

        AC: Then - 系统解析 JSON 文件内容
        """
        minimal_data = {
            "name": "最小配置",
            "description": "只包含必需字段",
            "stages": [
                {
                    "id": "stage_a",
                    "name": "阶段A",
                    "enabled": True,
                    "dependencies": []
                }
            ]
        }

        minimal_file = tmp_path / "minimal.json"
        with open(minimal_file, "w", encoding="utf-8") as f:
            json.dump(minimal_data, f)

        workflow, error_msg = load_custom_workflow(minimal_file)

        assert error_msg is None
        assert workflow is not None

        # 验证默认值
        assert workflow.id == "custom"  # 默认ID
        assert workflow.estimated_time == 0  # 默认时间

        # 验证阶段默认值
        assert len(workflow.stages) == 1
        assert workflow.stages[0].timeout == 300  # 默认超时时间
