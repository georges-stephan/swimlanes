from typing import cast

from swimlane.DiagramItems import DiagramItem


class Task(DiagramItem):

    def __init__(self, description: str):
        self.description = description
        self.order = -1 # not set
        self.new_location = -1 # not set

    def set_order(self, order: int):
        self.order = order

    def set_new_location(self,new_location: int):
        self.new_location = new_location

    def __str__(self):
        return f"Task description: {self.description}, order: {self.order}, new location: {self.new_location}"

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
