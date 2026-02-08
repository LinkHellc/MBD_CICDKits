from dataclasses import dataclass, field, fields

print(f"1. Before any class: list = {list}, type = {type(list)}")

@dataclass
class Test1:
    name: str = ""

print(f"2. After Test1: list = {list}, type = {type(list)}")

fields_result = fields(Test1)
print(f"3. After fields(Test1): list = {list}, type = {type(list)}")

@dataclass
class Test2:
    name: str = ""
    items: list = field(default_factory=list)

print(f"4. After Test2: list = {list}, type = {type(list)}")
print('All dataclasses created successfully')
