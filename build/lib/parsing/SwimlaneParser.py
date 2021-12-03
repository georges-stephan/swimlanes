from swimlane.Diagram import Diagram
from swimlane.Divider import Divider
from swimlane.Note import Note
from swimlane.Task import Task
from swimlane.TaskConnection import TaskConnection

starts_code = ["title:", "note:", "_:", "-:", "--:", "=:", "...:", "order:"]
arrow_operators = [" ->> ", " <<- ",
                   " --> ", " <-- ",
                   "-->>", "<<--",
                   " <-> ",
                   " -> ", " <- ",
                   " -x ", " x- ",
                   " => ", " <= "]
debug = False
diagram = Diagram("Diagram")
in_note = False
note_text = ""
note_task_from = -1
note_task_to = -1
task_number = 0


def load_file(file_path: str):
    with open(file_path, 'r') as f:
        file_content = f.read()

    lines = list(filter((lambda x: x.strip() != ''), file_content.splitlines()))
    if debug:
        print(len(lines))
        print(lines)

    return get_diagram_from_lines(lines)


def get_diagram_from_lines(lines: list):
    for line in lines:
        parse_line(line)

    return diagram


def get_diagram_from_string(design_as_string: str):
    lines = list(filter((lambda x: x.strip() != ''), design_as_string.splitlines()))
    if debug:
        print(len(lines))
        print(lines)

    return get_diagram_from_lines(lines)


def parse_line(line: str):
    if line.startswith("//"):  # Comment Line
        return
    if line.strip().lower() == 'autonumber':  # Mark tasks as needing auto-number
        diagram.auto_number = True
        return

    arrow = is_line_declaring_a_task_and_a_connection(line)

    global in_note
    global note_text
    global note_task_from
    global note_task_to
    global task_number

    if in_note and not is_code_line(line):  # In Note
        note_text += line
    elif in_note and is_code_line(line):  # End of Note
        if note_task_from == -1 and note_task_to == -1:
            diagram.add_diagram_item(Note(note_text))
        elif note_task_from != -1 and note_task_to == -1:
            diagram.add_diagram_item(Note(note_text, note_task_from, diagram.tasks_count - 1))
            note_task_from = -1
            note_task_to = -1
        else:
            diagram.add_diagram_item(Note(note_text, note_task_from, note_task_to))
            note_task_from = -1
            note_task_to = -1
            # TODO this is causing the parsing to skip the current line
        in_note = False
        parse_line(line)
    elif line.lower().startswith(starts_code[0]):  # Title
        diagram.title = line[6:len(line)]
    elif line.lower().startswith(starts_code[1]):  # Note Declaration
        # This is a new note
        in_note = True
        note_command = line[:line.find(':')]
        note_text = line[line.find(':') + 1:]

        note_commands = note_command.replace(',', ' ').split()

        if len(note_commands) == 1:  # Parsing note: blabla
            pass
            # note_task_from = -1
            # note_task_to = -1
        elif len(note_commands) == 2:  # Parsing note 1: blabla
            note_task_from = diagram.get_task_id(note_commands[1])
            note_task_to = -1
        elif len(note_commands) == 3:  # Parsing note 1,4: blabla
            note_task_from = diagram.get_task_id(note_commands[1])
            note_task_to = diagram.get_task_id(note_commands[2])
        else:
            raise ValueError(f"Error in file at line {line}, command is not know.")
    elif line.startswith(starts_code[2]):  # Thin Divider
        note_task_from = -1
        note_task_to = -1
        diagram.add_divider(Divider(line[2:len(line)], style="Thin"))
    elif line.startswith(starts_code[3]):  # Regular Divider
        note_task_from = -1
        note_task_to = -1
        diagram.add_divider(Divider(line[2:len(line)], style="Regular"))
        note_task_from = -1
        note_task_to = -1
    elif line.startswith(starts_code[4]):  # Dashed Divider
        diagram.add_divider(Divider(line[3:len(line)], style="Dashed"))
        note_task_from = -1
        note_task_to = -1
    elif line.startswith(starts_code[5]):  # Bold Divider
        diagram.add_divider(Divider(line[2:len(line)], style="Bold"))
        note_task_from = -1
        note_task_to = -1
    elif line.startswith(starts_code[6]):  # Delay Divider
        note_task_from = -1
        note_task_to = -1
        diagram.add_divider(Divider(line[4:len(line)], style="Delay"))
    elif line.startswith(starts_code[7]): # Order example usage: order: first [,second[,third ...]]
        order_command = line[:line.find(':')]
        order_text = line[line.find(':') + 1:]
        print(f"The order command is {order_command}, the parameters are {order_text}")
    elif arrow is not None:
        label, task_from_label, task_to_label = get_task_connection_from_input_line(line, arrow)
        task_from = Task(task_from_label)
        task_to = Task(task_to_label)

        diagram.add_diagram_item(task_from)
        diagram.add_diagram_item(task_to)

        # In case the connection is followed up by a note
        note_task_from = diagram.get_task_id(task_from)
        note_task_to = diagram.get_task_id(task_to)

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

        task_number += 1
        task_connection = TaskConnection(label, task_from, task_to, lost_message
                                         , style, bi_directional, open_arrow, diagram.auto_number, task_number)
        diagram.add_diagram_item(task_connection)


def is_line_declaring_a_task_and_a_connection(line: str):
    for arrow in arrow_operators:
        if line.find(arrow) >= 0:
            return arrow
    return None


def get_task_connection_from_input_line(line: str, arrow_operator: str):
    message_label = line[line.find(':') + 1:len(line)].strip()
    task_from = line[0:line.find(arrow_operator)].strip()
    task_to = line[line.find(arrow_operator) + len(arrow_operator):line.find(':')].strip()

    if debug:
        print(f"The message label is '{message_label}', Task FROM is '{task_from}', Task TO is '{task_to}'.")

    return message_label, task_from, task_to


def is_code_line(line: str):
    for sc in starts_code:
        if line.lower().startswith(sc):
            return True

    for ao in arrow_operators:
        if line.find(ao) and line.find(':') != -1:
            return True

    return False
