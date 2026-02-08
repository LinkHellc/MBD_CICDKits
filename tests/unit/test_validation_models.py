"""单元测试：验证数据模型

测试 ValidationError、ValidationResult 和 ValidationSeverity 数据模型。
"""

import pytest
from src.core.models import ValidationError, ValidationResult, ValidationSeverity


class TestValidationSeverity:
    """测试 ValidationSeverity 枚举"""

    def test_severity_enum_values(self):
        """测试枚举值是否正确"""
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"

    def test_severity_enum_comparison(self):
        """测试枚举比较"""
        assert ValidationSeverity.ERROR == ValidationSeverity.ERROR
        assert ValidationSeverity.ERROR != ValidationSeverity.WARNING


class TestValidationError:
    """测试 ValidationError dataclass"""

    def test_default_values(self):
        """测试默认值"""
        error = ValidationError()
        assert error.field == ""
        assert error.message == ""
        assert error.severity == ValidationSeverity.ERROR
        assert error.suggestions == []
        assert error.stage == ""

    def test_create_with_values(self):
        """测试创建带值的错误"""
        error = ValidationError(
            field="test_field",
            message="Test error message",
            severity=ValidationSeverity.WARNING,
            suggestions=["Suggestion 1", "Suggestion 2"],
            stage="test_stage"
        )
        assert error.field == "test_field"
        assert error.message == "Test error message"
        assert error.severity == ValidationSeverity.WARNING
        assert error.suggestions == ["Suggestion 1", "Suggestion 2"]
        assert error.stage == "test_stage"

    def test_to_dict(self):
        """测试转换为字典"""
        error = ValidationError(
            field="test_field",
            message="Test error message",
            severity=ValidationSeverity.ERROR,
            suggestions=["Suggestion 1"],
            stage="test_stage"
        )
        result = error.to_dict()
        assert result == {
            "field": "test_field",
            "message": "Test error message",
            "severity": "error",
            "suggestions": ["Suggestion 1"],
            "stage": "test_stage"
        }

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "field": "test_field",
            "message": "Test error message",
            "severity": "warning",
            "suggestions": ["Suggestion 1"],
            "stage": "test_stage"
        }
        error = ValidationError.from_dict(data)
        assert error.field == "test_field"
        assert error.message == "Test error message"
        assert error.severity == ValidationSeverity.WARNING
        assert error.suggestions == ["Suggestion 1"]
        assert error.stage == "test_stage"

    def test_from_dict_with_extra_fields(self):
        """测试从字典创建时过滤未知字段"""
        data = {
            "field": "test_field",
            "message": "Test error message",
            "severity": "error",
            "suggestions": [],
            "stage": "test_stage",
            "unknown_field": "should be filtered"
        }
        error = ValidationError.from_dict(data)
        assert not hasattr(error, "unknown_field")

    def test_severity_string_conversion(self):
        """测试严重级别字符串转换"""
        data = {
            "field": "test_field",
            "message": "Test error message",
            "severity": "error",
            "suggestions": [],
            "stage": ""
        }
        error = ValidationError.from_dict(data)
        assert error.severity == ValidationSeverity.ERROR
        assert isinstance(error.severity, ValidationSeverity)


class TestValidationResult:
    """测试 ValidationResult dataclass"""

    def test_default_values(self):
        """测试默认值"""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warning_count == 0
        assert result.error_count == 0

    def test_create_with_values(self):
        """测试创建带值的结果"""
        errors = [
            ValidationError(
                field="field1",
                message="Error 1",
                severity=ValidationSeverity.ERROR
            ),
            ValidationError(
                field="field2",
                message="Error 2",
                severity=ValidationSeverity.WARNING
            )
        ]
        result = ValidationResult(
            is_valid=False,
            errors=errors,
            warning_count=1,
            error_count=1
        )
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.warning_count == 1
        assert result.error_count == 1

    def test_to_dict(self):
        """测试转换为字典"""
        errors = [
            ValidationError(
                field="field1",
                message="Error 1",
                severity=ValidationSeverity.ERROR
            )
        ]
        result = ValidationResult(
            is_valid=False,
            errors=errors,
            warning_count=0,
            error_count=1
        )
        data = result.to_dict()
        assert data["is_valid"] is False
        assert len(data["errors"]) == 1
        assert data["warning_count"] == 0
        assert data["error_count"] == 1
        assert data["errors"][0]["severity"] == "error"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "is_valid": False,
            "errors": [
                {
                    "field": "field1",
                    "message": "Error 1",
                    "severity": "error",
                    "suggestions": [],
                    "stage": ""
                }
            ],
            "warning_count": 0,
            "error_count": 1
        }
        result = ValidationResult.from_dict(data)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.warning_count == 0
        assert result.error_count == 1
        assert result.errors[0].severity == ValidationSeverity.ERROR

    def test_from_dict_with_extra_fields(self):
        """测试从字典创建时过滤未知字段"""
        data = {
            "is_valid": True,
            "errors": [],
            "warning_count": 0,
            "error_count": 0,
            "unknown_field": "should be filtered"
        }
        result = ValidationResult.from_dict(data)
        assert not hasattr(result, "unknown_field")

    def test_add_error_error(self):
        """测试添加错误级别的错误"""
        result = ValidationResult()
        error = ValidationError(
            field="test_field",
            message="Test error",
            severity=ValidationSeverity.ERROR
        )
        result.add_error(error)
        assert result.is_valid is False
        assert result.error_count == 1
        assert result.warning_count == 0
        assert len(result.errors) == 1

    def test_add_error_warning(self):
        """测试添加警告级别的错误"""
        result = ValidationResult()
        error = ValidationError(
            field="test_field",
            message="Test warning",
            severity=ValidationSeverity.WARNING
        )
        result.add_error(error)
        assert result.is_valid is True  # 警告不阻止执行
        assert result.error_count == 0
        assert result.warning_count == 1
        assert len(result.errors) == 1

    def test_add_error_info(self):
        """测试添加信息级别的错误"""
        result = ValidationResult()
        error = ValidationError(
            field="test_field",
            message="Test info",
            severity=ValidationSeverity.INFO
        )
        result.add_error(error)
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.errors) == 1

    def test_add_multiple_errors(self):
        """测试添加多个错误"""
        result = ValidationResult()
        result.add_error(ValidationError(
            field="field1",
            message="Error 1",
            severity=ValidationSeverity.ERROR
        ))
        result.add_error(ValidationError(
            field="field2",
            message="Warning 1",
            severity=ValidationSeverity.WARNING
        ))
        result.add_error(ValidationError(
            field="field3",
            message="Error 2",
            severity=ValidationSeverity.ERROR
        ))
        assert result.is_valid is False
        assert result.error_count == 2
        assert result.warning_count == 1
        assert len(result.errors) == 3

    def test_get_errors_by_severity_error(self):
        """测试按严重级别获取错误（ERROR）"""
        result = ValidationResult()
        result.add_error(ValidationError(
            field="field1",
            message="Error 1",
            severity=ValidationSeverity.ERROR
        ))
        result.add_error(ValidationError(
            field="field2",
            message="Warning 1",
            severity=ValidationSeverity.WARNING
        ))
        errors = result.get_errors_by_severity(ValidationSeverity.ERROR)
        assert len(errors) == 1
        assert errors[0].field == "field1"

    def test_get_errors_by_severity_warning(self):
        """测试按严重级别获取错误（WARNING）"""
        result = ValidationResult()
        result.add_error(ValidationError(
            field="field1",
            message="Error 1",
            severity=ValidationSeverity.ERROR
        ))
        result.add_error(ValidationError(
            field="field2",
            message="Warning 1",
            severity=ValidationSeverity.WARNING
        ))
        result.add_error(ValidationError(
            field="field3",
            message="Warning 2",
            severity=ValidationSeverity.WARNING
        ))
        errors = result.get_errors_by_severity(ValidationSeverity.WARNING)
        assert len(errors) == 2
        assert errors[0].field == "field2"
        assert errors[1].field == "field3"

    def test_get_errors_by_severity_info(self):
        """测试按严重级别获取错误（INFO）"""
        result = ValidationResult()
        result.add_error(ValidationError(
            field="field1",
            message="Info 1",
            severity=ValidationSeverity.INFO
        ))
        errors = result.get_errors_by_severity(ValidationSeverity.INFO)
        assert len(errors) == 1

    def test_valid_result_with_warnings(self):
        """测试有警告但有效的结果"""
        result = ValidationResult()
        result.add_error(ValidationError(
            field="field1",
            message="Warning 1",
            severity=ValidationSeverity.WARNING
        ))
        result.add_error(ValidationError(
            field="field2",
            message="Warning 2",
            severity=ValidationSeverity.WARNING
        ))
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count == 2
