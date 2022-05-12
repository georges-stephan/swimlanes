import io
import logging

from swimlane.DiagramItems import DiagramItem
from swimlane.Divider import Divider
from swimlane.Note import Note
from swimlane.Task import Task
from swimlane.TaskConnection import TaskConnection

logger = logging.getLogger(__name__)


class Diagram:

    def __init__(self, title: str):
        self.title = title
        self.items_count = 0
        self.tasks_count = 0
        self.dividers_count = 0
        self.task_connections_count = 0
        self.notes_count = 0
        self.auto_number = False
        self.swapped_items = {}
        self.items = {}

    def add_diagram_item(self, diagram_item: DiagramItem):
        if isinstance(diagram_item, Task):
            self.add_task(diagram_item)
        elif isinstance(diagram_item, Divider):
            self.add_divider(diagram_item)
        elif isinstance(diagram_item, TaskConnection):
            self.add_task_connection(diagram_item)
        elif isinstance(diagram_item, Note):
            self.add_note(diagram_item)

    def get_item_index_for_task_number(self, task_index: int):
        item_counter = 0
        task_counter = 0
        for key in self.items:
            if isinstance(self.items[key], Task):
                if task_counter == task_index:
                    return item_counter + 1
                else:
                    task_counter += 1
                    item_counter += 1
            else:
                item_counter += 1
        raise Exception(f"Can't find a task with index {task_index}.")

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

    def __get_diagram_task_index(self, task: Task):
        """
        <b>Does not consider the re-ordering index of tasks</b>
        :param task:
        :return: the index of the given task.
        """
        for key in self.items:
            if isinstance(self.items[key], Task):
                if self.items[key] == task:
                    return key
        return -1

    def get_task_by_index(self, task_number: int):
        """

        :param task_number: task index
        :return: a task
        """
        task_number_counter = 0
        for key in self.items:
            task = self.items[key]
            if isinstance(task, Task):
                if task_number == task_number_counter:
                    return task
                else:
                    task_number_counter += 1
        return None

    def get_task_id(self, task: Task):  # TODO test me
        task_id = 0
        for key in self.items:
            if isinstance(self.items[key], Task):
                if self.items[key] == task:
                    return task_id
                else:
                    task_id += 1
        return -1

    def apply_order(self, items_oder: [str]):
        temp = [0] * len(items_oder)

        i = 0
        for task_name in items_oder:
            temp[i] = self.get_task_id(self.get_task_by_name(task_name))
            i += 1

        self.__reorder(temp)

    def __reorder(self, index: [int]):  # Fuck

        temp = {}
        n = len(self.items) + 1

        # items[i] should be
        # present at index[i] index
        j = 0
        for i in range(1, n):

            if isinstance(self.items[i], Task):
                item_index = self.get_item_index_for_task_number(index[j])
                if item_index in temp:
                    raise Exception(f"Entry {item_index} is not empty (has {self.items[item_index]} at iteration {i}.")
                temp[item_index] = self.items[i]
                j += 1
            else:
                temp[i] = self.items[i]

        # Copy temp[] to items[]
        for i in range(1, n):
            self.items[i] = temp[i]

    def print_tasks(self):
        index = 0
        for key in self.items:
            if isinstance(self.items[key], Task):
                logger.info(f"At {index}, task is {str(self.items[key])}.")
                index += 1

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        diagram_as_text = io.StringIO()

        for key in self.items:
            diagram_as_text.write(str(self.items[key]))

        return diagram_as_text.getvalue()
