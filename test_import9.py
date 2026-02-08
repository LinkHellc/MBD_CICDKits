from dataclasses import dataclass, field, fields

print(f"1. Start: list = {list}, type = {type(list)}")

@dataclass
class ProjectConfig:
    name: str = ""

print(f"2. After ProjectConfig: list = {list}, type = {type(list)}")

@dataclass
class ValidationError:
    field: str = ""
    suggestions: list = field(default_factory=list)

print(f"3. After ValidationError: list = {list}, type = {type(list)}")
print('All dataclasses created successfully')
