"""Unit tests for parsing workflow configuration (Story 2.2)

This module tests the workflow configuration parsing functionality
"""

import json
import logging
import pytest
from pathlib import Path

from core.models import WorkflowConfig, StageConfig

logger = logging.getLogger(__name__)


class TestParseWorkflowConfig:
    """Test suite for parsing WorkflowConfig from dictionaries"""

    def test_parse_valid_workflow_dict(self):
        """Test parsing a valid workflow configuration dictionary

        AC: Then - 系统解析 JSON 文件内容
        """
        workflow_dict = {
            "id": "test_workflow",
            "name": "测试工作流",
            "description": "这是一个测试工作流",
            "estimated_time": 10,
            "stages": [
                {
                    "name": "matlab_gen",
                    "enabled": True,
                    "timeout": 1800
                },
                {
                    "name": "file_process",
                    "enabled": True,
                    "timeout": 300
                }
            ]
        }

        workflow = WorkflowConfig.from_dict(workflow_dict)

        assert workflow.id == "test_workflow"
        assert workflow.name == "测试工作流"
        assert workflow.description == "这是一个测试工作流"
        assert workflow.estimated_time == 10
        assert len(workflow.stages) == 2

    def test_parse_workflow_with_default_values(self):
        """Test parsing workflow with missing optional fields

        AC: Task 4.3 - 确保所有字段提供默认值
        """
        workflow_dict = {
            "name": "最小工作流",
            "stages": []
        }

        workflow = WorkflowConfig.from_dict(workflow_dict)

        # 验证默认值
        assert workflow.id == ""
        assert workflow.description == ""
        assert workflow.estimated_time == 0
        assert workflow.stages == []

    def test_parse_workflow_with_nested_stages(self):
        """Test parsing workflow with nested stage configurations

        AC: Task 4.2 - 确保支持从 JSON 字典创建 WorkflowConfig 对象
        """
        workflow_dict = {
            "id": "nested_test",
            "name": "嵌套测试",
            "stages": [
                {
                    "name": "stage1",
                    "enabled": True,
                    "timeout": 100
                },
                {
                    "name": "stage2",
                    "enabled": False,
                    "timeout": 200
                }
            ]
        }

        workflow = WorkflowConfig.from_dict(workflow_dict)

        assert len(workflow.stages) == 2

        # 验证第一个阶段
        assert workflow.stages[0].name == "stage1"
        assert workflow.stages[0].enabled == True
        assert workflow.stages[0].timeout == 100

        # 验证第二个阶段
        assert workflow.stages[1].name == "stage2"
        assert workflow.stages[1].enabled == False
        assert workflow.stages[1].timeout == 200

    def test_parse_stage_config(self):
        """Test parsing individual stage configuration

        AC: Task 4.2 - 确保支持从 JSON 字典创建 WorkflowConfig 对象
        """
        stage_dict = {
            "name": "test_stage",
            "enabled": True,
            "timeout": 600
        }

        stage = StageConfig.from_dict(stage_dict)

        assert stage.name == "test_stage"
        assert stage.enabled == True
        assert stage.timeout == 600

    def test_parse_stage_with_defaults(self):
        """Test parsing stage with missing optional fields

        AC: Task 4.3 - 确保所有字段提供默认值
        """
        stage_dict = {
            "name": "minimal_stage",
            "enabled": False
        }

        stage = StageConfig.from_dict(stage_dict)

        assert stage.name == "minimal_stage"
        assert stage.enabled == False
        assert stage.timeout == 300  # 默认超时时间

    def test_serialize_workflow_to_dict(self):
        """Test serializing workflow configuration back to dictionary

        AC: Task 4.2 - 确保支持从 JSON 字典创建 WorkflowConfig 对象
        """
        workflow = WorkflowConfig(
            id="serialize_test",
            name="序列化测试",
            description="测试序列化功能",
            estimated_time=15,
            stages=[
                StageConfig(name="stage1", enabled=True, timeout=100),
                StageConfig(name="stage2", enabled=False, timeout=200)
            ]
        )

        workflow_dict = workflow.to_dict()

        assert workflow_dict["id"] == "serialize_test"
        assert workflow_dict["name"] == "序列化测试"
        assert workflow_dict["description"] == "测试序列化功能"
        assert workflow_dict["estimated_time"] == 15
        assert len(workflow_dict["stages"]) == 2

    def test_serialize_stage_to_dict(self):
        """Test serializing stage configuration back to dictionary

        AC: Task 4.2 - 确保支持从 JSON 字典创建 WorkflowConfig 对象
        """
        stage = StageConfig(
            name="serialize_stage",
            enabled=True,
            timeout=500
        )

        stage_dict = stage.to_dict()

        assert stage_dict["name"] == "serialize_stage"
        assert stage_dict["enabled"] == True
        assert stage_dict["timeout"] == 500

    def test_round_trip_workflow(self):
        """Test parsing and serializing workflow (round-trip)

        AC: Task 4.2 - 确保支持从 JSON 字典创建 WorkflowConfig 对象
        """
        original_dict = {
            "id": "round_trip_test",
            "name": "往返测试",
            "description": "测试往返序列化",
            "estimated_time": 20,
            "stages": [
                {"name": "stage1", "enabled": True, "timeout": 100},
                {"name": "stage2", "enabled": False, "timeout": 200}
            ]
        }

        # 解析
        workflow = WorkflowConfig.from_dict(original_dict)

        # 序列化
        result_dict = workflow.to_dict()

        # 验证往返结果一致
        assert result_dict == original_dict

    def test_filter_unknown_fields(self):
        """Test that unknown fields are filtered out during parsing

        AC: Task 4.1 - 确认 models.py 中已有 WorkflowConfig 和 StageConfig
        """
        workflow_dict_with_unknown = {
            "id": "test",
            "name": "测试",
            "unknown_field": "should_be_ignored",
            "another_unknown": 123,
            "stages": []
        }

        workflow = WorkflowConfig.from_dict(workflow_dict_with_unknown)

        # 验证未知字段被过滤
        assert not hasattr(workflow, "unknown_field")
        assert not hasattr(workflow, "another_unknown")

        # 验证已知字段正确
        assert workflow.id == "test"
        assert workflow.name == "测试"

    def test_filter_unknown_stage_fields(self):
        """Test that unknown stage fields are filtered out

        AC: Task 4.1 - 确认 models.py 中已有 WorkflowConfig 和 StageConfig
        """
        stage_dict_with_unknown = {
            "name": "test_stage",
            "enabled": True,
            "unknown_stage_field": "ignored",
            "stages": []
        }

        stage = StageConfig.from_dict(stage_dict_with_unknown)

        # 验证未知字段被过滤
        assert not hasattr(stage, "unknown_stage_field")

        # 验证已知字段正确
        assert stage.name == "test_stage"
        assert stage.enabled == True
