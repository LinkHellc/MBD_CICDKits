from dataclasses import dataclass, field
from typing import List

@dataclass
class Test:
    items: List[str] = field(default_factory=list)

print('Dataclass created successfully')
