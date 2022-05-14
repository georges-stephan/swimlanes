from typing import cast

from swimlane.DiagramItems import DiagramItem


class Task(DiagramItem):

    def __init__(self, description: str):
        self.description = description

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Task description: {self.description}."

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, Task):
            return False

        if self.description == cast(Task, other).description:
            return True
        else:
            return False

        return False
