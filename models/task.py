from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    priority: Optional[str] = None
    project: Optional[str] = None
    tags: list[str] | None = None