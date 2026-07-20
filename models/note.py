from dataclasses import dataclass
from typing import Optional

@dataclass
class Note:
    title: str
    content: str
    category: str | None
    project: str | None
    tags: list[str]