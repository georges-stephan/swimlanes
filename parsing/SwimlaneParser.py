from configparser import ParsingError

from parsing import constant
from swimlane.Diagram import Diagram
from swimlane.Divider import Divider
from swimlane.Note import Note
from swimlane.Task import Task
from swimlane.TaskConnection import TaskConnection

import logging
logger = logging.getLogger(__name__)


def is_code_line(line: str):
    for sc in constant.START_CODE:
        if line.lower().startswith(sc):
            return True

    for ao in constant.ARROW_OPERATORS:
        if line.find(ao) and line.find(':') != -1:
            return True

    return False


def get_task_connection_from_input_line(line: str, an_arrow_operator: str):
    message_label = line[line.find(':') + 1:len(line)].strip()
    task_from = line[0:line.find(an_arrow_operator)].strip()
    task_to = line[line.find(an_arrow_operator) + len(an_arrow_operator):line.find(':')].strip()

    logger.debug(f"The message label is '{message_label}', Task FROM is '{task_from}', Task TO is '{task_to}'.")

    return message_label, task_from, task_to


def is_line_declaring_a_task_and_a_connection(line: str):
    for arrow in constant.ARROW_OPERATORS:
        if line.find(arrow) >= 0:
            return arrow
    return None


class SwimlaneParser:

    def __init__(self, diagram_name="Diagram"):
        self.diagram_name = diagram_name
        self.diagram = Diagram(diagram_name)
        self.in_note = False
        self.note_text = ""
        self.note_task_from = -1
        self.note_task_to = -1
        self.task_number = 0

    def load_file(self, file_path: str):
        with open(file_path, 'r') as f:
            file_content = f.read()

        lines = list(filter((lambda x: x.strip() != ''), file_content.splitlines()))
        logger.debug(f" Got {len(lines)} number of lines which are:{lines}")

        self.reset_attributes()
        return self.get_diagram_from_lines(lines)

    def reset_attributes(self):
        self.diagram = Diagram(self.diagram_name)
        self.in_note = False
        self.note_text = ""
        self.note_task_from = -1
        self.note_task_to = -1
        self.task_number = 0

    def get_diagram_from_lines(self, lines: list):
        line_number = 1
        for line in lines:
            self.parse_line(line, line_number) # Used to strip the line, but it interferences with note's text
            line_number += 1

        # Since notes can span over multiple lines, we need to check if the last line/command was part of node
        # and if so, add the note to the diagram
        if self.in_note:
            self.diagram.add_diagram_item(Note(self.note_text, self.note_task_from, self.note_task_to))

        return self.diagram

    def parse_line(self, line: str, line_number: int):
        if line.startswith("//"):  # Comment Line
            return
        if line.strip().lower() == 'autonumber':  # Mark tasks as needing auto-number
            self.diagram.auto_number = True
            return

        arrow = is_line_declaring_a_task_and_a_connection(line)

        if self.in_note and not is_code_line(line):  # In Note
            self.note_text += line
        elif self.in_note and is_code_line(line):  # End of Note
            if self.note_task_from == -1 and self.note_task_to == -1:
                self.diagram.add_diagram_item(Note(self.note_text))
            elif self.note_task_from != -1 and self.note_task_to == -1:
                self.diagram.add_diagram_item(Note(self.note_text, self.note_task_from, self.diagram.tasks_count - 1))
                self.note_task_from = -1
                self.note_task_to = -1
            else:
                self.diagram.add_diagram_item(Note(self.note_text, self.note_task_from, self.note_task_to))
                self.note_task_from = -1
                self.note_task_to = -1
            self.in_note = False
            self.note_text = ""

            # In the previous iteration, we had a one-line comment, so we are in comment mode. Since the current line
            # has a command in it, we need to turn off the in comment mode and re-invoke the same function
            self.parse_line(line,line_number)
        elif line.lower().startswith(constant.START_CODE[0]):  # Title
            self.diagram.title = line[6:len(line)]
        elif line.lower().startswith(constant.START_CODE[1]):  # Note Declaration
            # This is a new note. Extended format of the note is:
            # note 1,9: Some text note

            self.in_note = True
            note_command = line[:line.find(':')]
            self.note_text = self.note_text + line[line.find(':') + 1:]

            # Check if the user specified the start and optionally the end task id
            note_boundaries = note_command.replace(',', ' ').split()

            if len(note_boundaries) == 1: # Parsing note: Some text
                # No start or end task specified, the will horizontally fill the entire diagram
                # TODO when no boundaries are specified, get the "node from" and "node to" of the previous arrow entry
                self.note_task_from, self.note_task_to = self.diagram.get_last_arrow_connections()

            elif len(note_boundaries) == 2:  # Parsing note 1: Some text
                self.note_task_from = int(note_boundaries[1])
                self.note_task_to = -1

            elif len(note_boundaries) == 3:  # Parsing note 1,4: Some text
                if int(note_boundaries[1]) < 0:
                    raise ParsingError(f"At line {line_number}:Note boundaries should be a positive integer, not"
                                       f"{note_boundaries[1]}")
                if int(note_boundaries[2]) < int(note_boundaries[1]):
                    raise ParsingError(f"At line {line_number}:Second note boundary:{note_boundaries[2]} cannot be "
                                       f"smaller than the first:{note_boundaries[1]}.")
                if int(note_boundaries[2]) == int(note_boundaries[1]):
                    raise ParsingError(f"At line {line_number}:Note boundary should not be equal:{note_boundaries[1]}.")

                self.note_task_from = int(note_boundaries[1])
                self.note_task_to = int(note_boundaries[2])
            else:
                raise ValueError(f"Error in file at line {line}, command is not know.")
        elif line.startswith(constant.START_CODE[2]):  # Thin Divider
            self.diagram.add_divider(Divider(line[2:len(line)], style="Thin"))
        elif line.startswith(constant.START_CODE[3]):  # Regular Divider
            self.diagram.add_divider(Divider(line[2:len(line)], style="Regular"))
        elif line.startswith(constant.START_CODE[4]):  # Dashed Divider
            self.diagram.add_divider(Divider(line[3:len(line)], style="Dashed"))
        elif line.startswith(constant.START_CODE[5]):  # Bold Divider
            self.diagram.add_divider(Divider(line[2:len(line)], style="Bold"))
        elif line.startswith(constant.START_CODE[6]):  # Delay Divider
            self.diagram.add_divider(Divider(line[4:len(line)], style="Delay"))
        elif line.startswith(constant.START_CODE[7]):  # Order example usage: order: first [,second[,third ...]]
            order_text = line[line.find(':') + 1:]

            items_order = order_text.split(",")
            self.diagram.apply_order(items_order)
            self.diagram.print_tasks()
        elif arrow is not None:
            label, task_from_label, task_to_label = get_task_connection_from_input_line(line, arrow)
            task_from = Task(task_from_label)
            task_to = Task(task_to_label)

            self.diagram.add_diagram_item(task_from)
            self.diagram.add_diagram_item(task_to)

            if arrow.find('x') != -1:
                lost_message = True
            else:
                lost_message = False

            style = 'regular'
            if arrow.find('--') != -1:
                style = 'dashed'
            elif arrow.find('=') != -1:
                style = 'bold'

            if arrow == '<->':
                bi_directional = True
            else:
                bi_directional = False

            if arrow.find('<<') != -1 or arrow.find('>>') != -1:
                open_arrow = True
            else:
                open_arrow = False

            self.task_number += 1
            task_connection = TaskConnection(label, task_from, task_to, lost_message
                                             , style, bi_directional, open_arrow, self.diagram.auto_number,
                                             self.task_number)
            self.diagram.add_diagram_item(task_connection)
