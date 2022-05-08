from swimlane.DiagramItems import DiagramItem


class Note(DiagramItem):

    def __init__(self, note_text: str, start_task_id=-1, end_task_id=-1):
        self.note_text = note_text

        self.__start_task_id = start_task_id
        self.__end_task_id = end_task_id

        self.__arrange_orders()

    def __arrange_orders(self):
        if self.__end_task_id < self.__start_task_id:
            temp = self.__start_task_id
            self.__start_task_id = self.__end_task_id
            self.__end_task_id = temp

    def get_start_task_id(self):
        return self.__start_task_id

    def get_end_task_id(self):
        return self.__end_task_id

    def set_start_task_id(self, start_task_id: int):
        self.__start_task_id = start_task_id
        self.__arrange_orders()

    def set_end_task_id(self, end_task_id: int):
        self.__end_task_id = end_task_id
        self.__arrange_orders()

    def is_boundary_defined(self):
        if self.__start_task_id>-1 and self.__end_task_id>-1:
            pass
            # return True
        return False

    def __str__(self):
        return f"Note starts from  task #{self.__start_task_id} to task #{self.__end_task_id}, text is {self.note_text}."
