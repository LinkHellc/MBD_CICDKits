"""Unit tests for custom workflow loader (Story 2.2)."""

import pytest
import tempfile
import json
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.config import load_custom_workflow
from core.models import WorkflowConfig


class TestLoadCustomWorkflow:
    """测试自定义工作流加载器 (Story 2.2)"""

    def test_load_custom_workflow_exists(self):
        """测试 load_custom_workflow 函数存在

        Given: core.config 模块
        Then: load_custom_workflow 函数应存在
        """
        from core.config import load_custom_workflow
        assert callable(load_custom_workflow)

    def test_load_custom_workflow_valid_json(self):
        """测试加载有效的自定义工作流配置

        Given: 一个有效的自定义工作流JSON文件
        When: 调用 load_custom_workflow()
        Then: 应成功返回 WorkflowConfig 对象，error_message 为 None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            valid_config = {
                "name": "自定义工作流",
                "description": "测试工作流描述",
                "estimated_time": 20,
                "stages": [
                    {
                        "id": "stage1",
                        "name": "阶段1",
                        "enabled": True,
                        "dependencies": []
                    },
                    {
                        "id": "stage2",
                        "name": "阶段2",
                        "enabled": True,
                        "dependencies": ["stage1"]
                    }
                ]
            }
            json.dump(valid_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is not None
            assert error_msg is None
            assert isinstance(workflow, WorkflowConfig)
            assert workflow.name == "自定义工作流"
            assert len(workflow.stages) == 2
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_invalid_json(self):
        """测试加载无效的JSON格式

        Given: 一个格式错误的JSON文件
        When: 调用 load_custom_workflow()
        Then: 应返回错误信息，workflow 为 None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "JSON格式错误" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_missing_required_fields(self):
        """测试缺少必需字段

        Given: 一个缺少必需字段的JSON文件
        When: 调用 load_custom_workflow()
        Then: 应返回包含字段名称的错误信息
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            invalid_config = {
                "name": "测试工作流"
                # 缺少 description 和 stages
            }
            json.dump(invalid_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "缺少必需字段" in error_msg
            assert "description" in error_msg or "stages" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_empty_stages(self):
        """测试空的stages列表

        Given: 一个stages为空的JSON文件
        When: 调用 load_custom_workflow()
        Then: 应返回错误信息
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            invalid_config = {
                "name": "测试工作流",
                "description": "测试描述",
                "stages": []
            }
            json.dump(invalid_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "不能为空" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_stage_missing_fields(self):
        """测试阶段缺少必需字段

        Given: 一个stage缺少必需字段的JSON文件
        When: 调用 load_custom_workflow()
        Then: 应返回错误信息
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            invalid_config = {
                "name": "测试工作流",
                "description": "测试描述",
                "stages": [
                    {
                        "id": "stage1"
                        # 缺少 name, enabled, dependencies
                    }
                ]
            }
            json.dump(invalid_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "缺少必需字段" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_circular_dependencies(self):
        """测试循环依赖检测

        Given: 一个包含循环依赖的工作流配置
        When: 调用 load_custom_workflow()
        Then: 应返回包含循环依赖错误的信息
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            circular_config = {
                "name": "循环依赖测试",
                "description": "测试循环依赖检测",
                "stages": [
                    {
                        "id": "stage1",
                        "name": "阶段1",
                        "enabled": True,
                        "dependencies": ["stage2"]
                    },
                    {
                        "id": "stage2",
                        "name": "阶段2",
                        "enabled": True,
                        "dependencies": ["stage1"]
                    }
                ]
            }
            json.dump(circular_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "循环依赖" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_invalid_dependency_reference(self):
        """测试无效的依赖引用

        Given: 一个引用不存在阶段ID的依赖
        When: 调用 load_custom_workflow()
        Then: 应返回包含依赖错误的信息
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            invalid_config = {
                "name": "无效依赖测试",
                "description": "测试无效依赖引用",
                "stages": [
                    {
                        "id": "stage1",
                        "name": "阶段1",
                        "enabled": True,
                        "dependencies": ["nonexistent_stage"]
                    }
                ]
            }
            json.dump(invalid_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "不存在" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_no_enabled_stages(self):
        """测试没有启用的阶段

        Given: 一个所有阶段都被禁用的工作流配置
        When: 调用 load_custom_workflow()
        Then: 应返回错误信息
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            invalid_config = {
                "name": "无启用阶段测试",
                "description": "测试无启用阶段",
                "stages": [
                    {
                        "id": "stage1",
                        "name": "阶段1",
                        "enabled": False,
                        "dependencies": []
                    }
                ]
            }
            json.dump(invalid_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is None
            assert error_msg is not None
            assert "至少需要启用一个阶段" in error_msg
        finally:
            temp_path.unlink()

    def test_load_custom_workflow_file_not_exists(self):
        """测试文件不存在

        Given: 一个不存在的文件路径
        When: 调用 load_custom_workflow()
        Then: 应返回错误信息
        """
        non_existent_path = Path("/tmp/this_file_does_not_exist.json")
        workflow, error_msg = load_custom_workflow(non_existent_path)
        assert workflow is None
        assert error_msg is not None
        assert "不存在" in error_msg

    def test_load_custom_workflow_complex_workflow(self):
        """测试复杂的多阶段工作流

        Given: 一个包含多个阶段和复杂依赖的工作流配置
        When: 调用 load_custom_workflow()
        Then: 应成功加载所有阶段和依赖关系
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            complex_config = {
                "name": "复杂工作流",
                "description": "包含5个阶段的完整工作流",
                "estimated_time": 25,
                "stages": [
                    {
                        "id": "matlab_gen",
                        "name": "MATLAB代码生成",
                        "enabled": True,
                        "dependencies": [],
                        "timeout": 1800
                    },
                    {
                        "id": "file_process",
                        "name": "文件处理",
                        "enabled": True,
                        "dependencies": ["matlab_gen"],
                        "timeout": 300
                    },
                    {
                        "id": "iar_compile",
                        "name": "IAR编译",
                        "enabled": True,
                        "dependencies": ["file_process"],
                        "timeout": 1200
                    },
                    {
                        "id": "a2l_process",
                        "name": "A2L处理",
                        "enabled": True,
                        "dependencies": ["iar_compile"],
                        "timeout": 600
                    },
                    {
                        "id": "package",
                        "name": "打包",
                        "enabled": True,
                        "dependencies": ["iar_compile", "a2l_process"],
                        "timeout": 60
                    }
                ]
            }
            json.dump(complex_config, f)
            temp_path = Path(f.name)

        try:
            workflow, error_msg = load_custom_workflow(temp_path)
            assert workflow is not None
            assert error_msg is None
            assert workflow.name == "复杂工作流"
            assert len(workflow.stages) == 5
            assert workflow.estimated_time == 25
        finally:
            temp_path.unlink()
