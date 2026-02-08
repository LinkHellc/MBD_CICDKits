"""Unit tests for validating workflow format (Story 2.2)

This module tests the workflow format validation functionality
"""

import json
import logging
import pytest
from pathlib import Path

from core.config import load_custom_workflow

logger = logging.getLogger(__name__)


class TestValidateWorkflowFormat:
    """Test suite for workflow format validation"""

    def test_validate_workflow_has_required_fields(self, tmp_path):
        """Test validating workflow has all required fields

        AC: Task 3.2 - 检查必需的字段是否存在（id, name, stages）
        """
        # 缺少 "name" 字段
        invalid_data = {
            "id": "test",
            "description": "缺少name",
            "stages": [
                {
                    "id": "stage1",
                    "name": "阶段1",
                    "enabled": True,
                    "dependencies": []
                }
            ]
        }

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "缺少必需字段" in error_msg
        assert "name" in error_msg

    def test_validate_stages_list_structure(self, tmp_path):
        """Test validating stages list structure

        AC: Task 3.3 - 检查 stages 列表结构是否正确
        """
        # stages 不是列表
        invalid_data = {
            "name": "无效stages",
            "description": "stages不是列表",
            "stages": "not_a_list"
        }

        invalid_file = tmp_path / "invalid_stages.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "stages" in error_msg
        assert "列表" in error_msg

    def test_validate_stage_required_fields(self, tmp_path):
        """Test validating each stage has required fields

        AC: Task 3.4 - 检查每个 stage 的必需字段
        """
        # 阶段缺少 "dependencies" 字段
        invalid_data = {
            "name": "无效阶段",
            "description": "阶段缺少字段",
            "stages": [
                {
                    "id": "stage1",
                    "name": "阶段1",
                    "enabled": True
                    # 缺少 dependencies
                }
            ]
        }

        invalid_file = tmp_path / "invalid_stage.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "缺少必需字段" in error_msg

    def test_validate_dependencies_field_type(self, tmp_path):
        """Test validating dependencies field type

        AC: Task 3.4 - 检查每个 stage 的必需字段
        """
        # dependencies 不是列表
        invalid_data = {
            "name": "无效依赖类型",
            "description": "dependencies不是列表",
            "stages": [
                {
                    "id": "stage1",
                    "name": "阶段1",
                    "enabled": True,
                    "dependencies": "not_a_list"
                }
            ]
        }

        invalid_file = tmp_path / "invalid_dep_type.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "dependencies" in error_msg
        assert "列表" in error_msg

    def test_validate_dependency_exists(self, tmp_path):
        """Test validating that referenced dependencies exist

        AC: Task 3.4 - 检查每个 stage 的必需字段
        """
        invalid_data = {
            "name": "不存在的依赖",
            "description": "引用不存在的阶段",
            "stages": [
                {
                    "id": "stage1",
                    "name": "阶段1",
                    "enabled": True,
                    "dependencies": ["non_existent_stage"]
                }
            ]
        }

        invalid_file = tmp_path / "nonexistent_dep.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        workflow, error_msg = load_custom_workflow(invalid_file)

        assert workflow is None
        assert error_msg is not None
        assert "不存在" in error_msg

    def test_validate_no_circular_dependencies(self, tmp_path):
        """Test validating no circular dependencies

        AC: Task 3.5 - 返回验证错误列表（空列表表示有效）
        """
        circular_data = {
            "name": "循环依赖",
            "description": "检测循环依赖",
            "stages": [
                {
                    "id": "a",
                    "name": "阶段A",
                    "enabled": True,
                    "dependencies": ["c"]
                },
                {
                    "id": "b",
                    "name": "阶段B",
                    "enabled": True,
                    "dependencies": ["a"]
                },
                {
                    "id": "c",
                    "name": "阶段C",
                    "enabled": True,
                    "dependencies": ["b"]
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

    def test_validate_at_least_one_enabled_stage(self, tmp_path):
        """Test validating at least one stage is enabled

        AC: Task 3.5 - 返回验证错误列表（空列表表示有效）
        """
        all_disabled_data = {
            "name": "全部禁用",
            "description": "所有阶段都被禁用",
            "stages": [
                {
                    "id": "stage1",
                    "name": "阶段1",
                    "enabled": False,
                    "dependencies": []
                },
                {
                    "id": "stage2",
                    "name": "阶段2",
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

    def test_valid_workflow_passes_validation(self, tmp_path):
        """Test that a valid workflow passes all validations

        AC: Task 3.5 - 返回验证错误列表（空列表表示有效）
        """
        valid_data = {
            "id": "valid_workflow",
            "name": "有效工作流",
            "description": "所有验证通过",
            "estimated_time": 10,
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
                }
            ]
        }

        valid_file = tmp_path / "valid.json"
        with open(valid_file, "w", encoding="utf-8") as f:
            json.dump(valid_data, f)

        workflow, error_msg = load_custom_workflow(valid_file)

        # 验证通过（error_msg为None表示有效）
        assert error_msg is None
        assert workflow is not None
        assert workflow.id == "valid_workflow"
        assert len(workflow.stages) == 3

    def test_validate_complex_dependency_chain(self, tmp_path):
        """Test validating complex dependency chains

        AC: Task 3.5 - 返回验证错误列表（空列表表示有效）
        """
        complex_data = {
            "name": "复杂依赖链",
            "description": "测试复杂的依赖关系",
            "stages": [
                {
                    "id": "a",
                    "name": "A",
                    "enabled": True,
                    "dependencies": []
                },
                {
                    "id": "b",
                    "name": "B",
                    "enabled": True,
                    "dependencies": ["a"]
                },
                {
                    "id": "c",
                    "name": "C",
                    "enabled": True,
                    "dependencies": ["a", "b"]
                },
                {
                    "id": "d",
                    "name": "D",
                    "enabled": True,
                    "dependencies": ["c"]
                },
                {
                    "id": "e",
                    "name": "E",
                    "enabled": False,
                    "dependencies": ["d"]
                }
            ]
        }

        complex_file = tmp_path / "complex.json"
        with open(complex_file, "w", encoding="utf-8") as f:
            json.dump(complex_data, f)

        workflow, error_msg = load_custom_workflow(complex_file)

        # 复杂依赖链应该通过验证
        assert error_msg is None
        assert workflow is not None
        assert len(workflow.stages) == 5
