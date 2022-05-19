from swimlane.DiagramItems import DiagramItem
from dataclasses import dataclass


@dataclass(slots=True)
class Task(DiagramItem):
    description: str
