from dataclasses import dataclass

@dataclass
class Note:
    title: str
    content: str
    category: str | None
    project: str | None
    tags: list[str]