import sys
sys.path.insert(0, 'D:\\BaiduSyncdisk\\4-学习\\100-项目\\181_CICDRedo\\src')

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

print(f"1. Before class definition: list = {list}, type = {type(list)}")

# 创建字段对象
suggestions_field = field(default_factory=list)
print(f"2. After creating field: list = {list}, type = {type(list)}")

@dataclass
class ValidationError:
    field: str = ""
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    suggestions: list = suggestions_field
    stage: str = ""

print(f"3. After class definition: list = {list}, type = {type(list)}")
print('Dataclass created successfully')
