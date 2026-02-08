from dataclasses import dataclass, field, fields

print(f"1. Start: list = {list}, type = {type(list)}")

@dataclass
class ValidationError:
    field: str = ""
    items: list = field(default_factory=list)

print(f"2. After ValidationError: list = {list}, type = {type(list)}")
print('All dataclasses created successfully')
