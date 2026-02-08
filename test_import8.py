from dataclasses import dataclass, field, fields
from typing import List
from enum import Enum

print(f"1. Start: list = {list}, type = {type(list)}")

@dataclass
class ProjectConfig:
    name: str = ""
    custom_params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None and v != ""}

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectConfig":
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

print(f"2. After ProjectConfig: list = {list}, type = {type(list)}")

@dataclass
class ValidationError:
    field: str = ""
    suggestions: list = field(default_factory=list)

print(f"3. After ValidationError: list = {list}, type = {type(list)}")
print('All dataclasses created successfully')
