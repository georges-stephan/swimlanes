import logging

from diagram.components.DiagramError import DiagramError
from diagram.components.DiagramItems import DiagramItem
from diagram.components.Divider import Divider
from diagram.components.Note import Note
from diagram.components.Task import Task
from diagram.components.TaskConnection import TaskConnection

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

        # Will be needed by by Note
        self.last_arrow_connection_from = 0
        self.last_arrow_connection_to = 0

    def add_diagram_item(self, diagram_item: DiagramItem):
        if isinstance(diagram_item, Task):
            self.add_task(diagram_item)
        elif isinstance(diagram_item, Divider):
            self.add_divider(diagram_item)
        elif isinstance(diagram_item, TaskConnection):
            self.add_task_connection(diagram_item)
        elif isinstance(diagram_item, Note):
            self.add_note(diagram_item)

    def get_id_of_last_task(self) -> int:
        last_task_id = -1
        for key in self.items:
            if isinstance(self.items[key], Task):
                last_task_id += 1

        if last_task_id == -1:
            raise DiagramError("No task was found in diagram")

        return last_task_id

    def get_first_task(self) -> Task:
        if self.tasks_count == 0:
            raise DiagramError("Diagram has no tasks attached.")
        else:
            for key in self.items:
                if isinstance(self.items[key], Task):
                    return self.items[key]
        raise DiagramError("No task was found in diagram")

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
        raise DiagramError(f"Can't find a task with index {task_index}.")

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

        # The coordinates of the last added connection is maintained so it can be used if a note is added
        self.last_arrow_connection_from = self.get_task_id(task_connection.source_task)
        self.last_arrow_connection_to = self.get_task_id(task_connection.target_task)

    def get_last_arrow_connections(self) -> (int, int):
        return self.last_arrow_connection_from, self.last_arrow_connection_to

    def add_note(self, note: Note):
        if note is None:
            return

        self.notes_count += 1
        self.items_count += 1
        self.items[self.items_count] = note

    def get_task_by_name(self, task_description: str) -> Task | None:
        """
        Returns a task given its description
        :param task_description:
        :return: the task
        """
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

    def get_task_by_index(self, task_number: int) -> Task | None:
        """
        Given a zero-based index, will return the task at this index
        :param task_number: task index, zero based
        :return: the task at this index
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

    def get_task_id(self, task: Task) -> int:  # TODO test me
        """
        Get the index of the task in the diagram
        :param task: a task object
        :return: 0 if it is the first task, 1 if it is the second, etc.
        """
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

    def __reorder(self, new_order_indexes: [int]):  # TODO still needs testing and probably fixing
        # example new_order_indexes was [0,3,1,2]
        diagram_tasks_items = []
        i = 0
        for _ in new_order_indexes:
            # Convert the relative task index to an  index in the graph
            # ie find the diagram item index
            diagram_task_item_id = self.get_item_index_for_task_number(new_order_indexes[i])
            diagram_tasks_items.append(diagram_task_item_id)
            i += 1

        # Here, diagram_tasks_items is [1, 8, 2, 4]
        # Diagram is                   [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # Diagram is                   [t, t, 3, t, 5, 6, 7, t, 9]

        temp = {}
        task_key = 1
        for key in self.items:
            if isinstance(self.items[key], Task):
                temp[key] = self.items[diagram_tasks_items[task_key - 1]]
                task_key += 1
            else:
                temp[key] = self.items[key]

        n = len(self.items) + 1
        for i in range(1, n):
            self.items[i] = temp[i]

    def print_tasks(self):
        index = 0
        for key in self.items:
            if isinstance(self.items[key], Task):
                logger.info(f"At {index}, task is {str(self.items[key])}.")
                index += 1
