import io

from swimlane.DiagramItems import DiagramItem
from swimlane.Divider import Divider
from swimlane.Note import Note
from swimlane.Task import Task
from swimlane.TaskConnection import TaskConnection


class Diagram:

    def __init__(self, title: str):
        self.title = title
        self.items = {}
        self.items_count = 0
        self.tasks_count = 0
        self.dividers_count = 0
        self.task_connections_count = 0
        self.notes_count = 0
        self.auto_number = False

    def add_diagram_item(self, diagram_item: DiagramItem):
        if isinstance(diagram_item, Task):
            self.add_task(diagram_item)
        elif isinstance(diagram_item, Divider):
            self.add_divider(diagram_item)
        elif isinstance(diagram_item, TaskConnection):
            self.add_task_connection(diagram_item)
        elif isinstance(diagram_item, Note):
            self.add_note(diagram_item)

    def add_task(self, task: Task):
        if task is None:
            return
        if self.get_task_id(task) != -1:
            # Task already added
            return

        self.tasks_count += 1
        self.items_count += 1
        self.items[self.items_count] = task

    def add_divider(self, divider: Divider):
        if divider is None:
            return

        self.dividers_count += 1
        self.items_count += 1
        self.items[self.items_count] = divider

    def add_task_connection(self, task_connection: TaskConnection):
        if task_connection is None:
            return

        self.task_connections_count += 1
        self.items_count += 1
        self.items[self.items_count] = task_connection

    def add_note(self, note: Note):
        if note is None:
            return

        self.notes_count += 1
        self.items_count += 1
        self.items[self.items_count] = note

    def get_task_id(self, task: Task):
        task_id = 0
        for key in self.items:
            if isinstance(self.items[key], Task):
                if self.items[key] == task:
                    return task_id
                else:
                    task_id += 1
        return -1

    def __str__(self):
        diagram_as_text = io.StringIO()

        for key in self.items:
            diagram_as_text.write(str(self.items[key]))

        return diagram_as_text.getvalue()
