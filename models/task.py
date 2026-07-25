from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Task:
    author_id: str
    title: str
    description: str | None = None
    priority: str | None = None
    due_date: str | None = None
    due_time: str | None = None
    project: str | None = None
    tags: list[str] = field(
        default_factory=list
    )