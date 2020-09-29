from typing import cast

from swimlane.DiagramItems import DiagramItem


class Task(DiagramItem):

    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        return "Task description: " + self.description + "."

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, Task):
            if self.description == cast(Task, other).description:
                return True
            else:
                return False
        else:
            return False
        return False
