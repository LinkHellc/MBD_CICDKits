import sys
sys.path.insert(0, 'D:\\BaiduSyncdisk\\4-学习\\100-项目\\181_CICDRedo\\src')

from dataclasses import dataclass, field
from dataclasses import fields
from typing import Optional
from enum import Enum

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

print(f"Before ValidationError: list = {list}, type = {type(list)}")

@dataclass
class ValidationError:
    field: str = ""
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    suggestions: list = field(default_factory=list)
    stage: str = ""

print(f"After ValidationError: list = {list}, type = {type(list)}")
print('Dataclass created successfully')
