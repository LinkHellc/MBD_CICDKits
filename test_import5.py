from dataclasses import field

print(f"field = {field}, type = {type(field)}")
print(f"list = {list}, type = {type(list)}")

result = field(default_factory=list)
print(f"field(default_factory=list) = {result}, type = {type(result)}")
