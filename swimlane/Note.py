from swimlane.DiagramItems import DiagramItem


class Note(DiagramItem):

    def __init__(self, note_text: str, start_task_id=-1, end_task_id=-1):
        self.note_text = note_text
        self.start_task_id = start_task_id
        self.end_task_id = end_task_id

    def __str__(self):
        return f"Note starts from  task #{self.start_task_id} to task #{self.end_task_id}, text is {self.note_text}."
