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
        self.swapped_items = {}

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
        task.order = self.items_count
        self.items[task.order] = task

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

    def get_task_by_name(self, task_description: str):
        for key in self.items:
            a_task = self.items[key]
            if isinstance(a_task, Task):
                if a_task.description.upper().strip() == task_description.upper().strip():
                    return a_task
        return None

    def get_diagram_task_index(self, task: Task):
        for key in self.items:
            if isinstance(self.items[key], Task):
                if self.items[key] == task:
                    return key
        return -1

    def get_task_by_index(self, task_number: int):
        task_number_counter = 0
        for key in self.items:
            task = self.items[key]
            if isinstance(task, Task):
                if task_number == task_number_counter:
                    return task
                else:
                    task_number_counter += 1
        return None

    def get_task_id(self, task: Task):
        task_id = 0
        for key in self.items:
            if isinstance(self.items[key], Task):
                if self.items[key] == task:
                    return task_id
                else:
                    task_id += 1
        return -1

    def apply_order(self, items_oder: [str]):
        index: int
        index = 0
        for item_name in items_oder:
            task = self.get_task_by_name(item_name)
            if task is not None:
                task.set_new_location(index)
            index += 1

        for key in self.items:
            task_a = self.items[key]
            if isinstance(task_a, Task):
                if task_a.new_location > -1:
                    task_b = self.get_task_by_index(task_a.new_location)
                    task_a_diagram_index = self.get_diagram_task_index(task_a)
                    task_b_diagram_index = self.get_diagram_task_index(task_b)

                    if task_a_diagram_index != task_b_diagram_index:
                        self.swapped_items[task_a_diagram_index] = task_b_diagram_index
                        self.swapped_items[task_b_diagram_index] = task_a_diagram_index

                    # Swap task_a and task_b
                    tmp = task_a
                    self.items[key] = task_b

                    if isinstance(self.items[task_b_diagram_index], Task):
                        self.items[task_b_diagram_index] = tmp
                    else:
                        raise Exception(
                            f"Iteration {key}:Can't replace Task with a {type(self.items[task_b_diagram_index])}.")

        # Notes are sensitive to tasks locations and need to be updated
        for key in self.items:
            a_note = self.items[key]
            if isinstance(a_note, Note):
                if a_note.get_start_task_id() in self.swapped_items:
                    a_note.set_start_task_id(self.swapped_items[a_note.get_start_task_id()])
                if a_note.get_end_task_id() in self.swapped_items:
                    a_note.set_end_task_id(self.swapped_items[a_note.get_end_task_id()])

    def print_tasks(self):
        for key in self.items:
            if isinstance(self.items[key], Task):
                print(str(self.items[key]))

    def __str__(self):
        diagram_as_text = io.StringIO()

        for key in self.items:
            diagram_as_text.write(str(self.items[key]))

        return diagram_as_text.getvalue()
