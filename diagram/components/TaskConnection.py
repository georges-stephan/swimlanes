from diagram.components.DiagramItems import DiagramItem
from diagram.components.Task import Task
from dataclasses import dataclass


def check_style(style: str):
    switcher = {"regular": 1, "dashed": 2, "bold": 3}
    i = switcher.get(style.lower(), 0)
    if i > 0:
        return True
    else:
        return False


@dataclass(slots=True)
class TaskConnection(DiagramItem):

    def __init__(self, label: str, source_task: Task, target_task: Task, lost_message=False, style="Regular",
                 bi_directional=False, open_arrow=False, auto_number=False, task_number=0):
        self.label = label
        self.source_task = source_task
        self.lost_message = lost_message
        self.style = style
        self.bi_directional = bi_directional
        self.open_arrow = open_arrow
        self.auto_number = auto_number
        self.task_number = task_number

        if check_style(style):
            pass
        else:
            raise TypeError(f"Un-supported style {style}. Supported styles are 'Regular', 'Dashed' and 'Bold'.")

        if target_task is None:
            self.looping_connection = True
        else:
            self.looping_connection = False
            self.target_task = target_task
