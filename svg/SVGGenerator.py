from templates.DefaultTemplate import DefaultTemplate
from svg.Errors import SVGSizeError
from swimlane.Diagram import Diagram
from functools import lru_cache
import io

from swimlane.Divider import Divider
from swimlane.Note import Note
from svg.FontFunctions import split_text, get_text_height
from swimlane.Task import Task
from swimlane.TaskConnection import TaskConnection

debug = False


def get_stroke_from_style_name(style_name: str):
    if style_name.lower() == "thin" or style_name.lower() == "delay":
        return 1, ''
    elif style_name.lower() == "regular":
        return 2, ''
    elif style_name.lower() == "bold":
        return 3, ''
    elif style_name.lower() == "dashed":
        return 3, 'stroke-dasharray=" 10 5"'
    else:
        raise ValueError(f"Unknown style {style_name}.")


class SVGRenderer:

    def __init__(self, diagram: Diagram, width: int, height: int, template=DefaultTemplate()):
        self.diagram = diagram
        self.width = width
        self.height = height
        self.template = template

        self.svg = io.StringIO()
        self.box_id = 0
        self.graph_items_height = {}

        self.preferred_height = 0

        # Add arrows style
        # Normal Arrow Style
        self.svg.write('<defs>\n')
        self.svg.write('<marker id="arrow_head" markerWidth="10" markerHeight="7" refX="3.5" refY="3.5" orient="auto">')
        self.svg.write('\n<polygon points="0 0, 10 3.5, 0 7"/>\n')
        self.svg.write('</marker>\n')

        # Lost Connection Arrow Style
        self.svg.write(
            '<marker id="lost_arrow_head" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">\n')
        self.svg.write(f'<line x1="0" y1="0" x2="10" y2="10" '
                       f'style="stroke:{self.template.get_parameter_value("connection_line_color")};'
                       f'stroke-width:{self.template.get_parameter_value("arrow_stroke_width")}"/>\n')
        self.svg.write(f'<line x1="0" y1="10" x2="10" y2="0" '
                       f'style="stroke:{self.template.get_parameter_value("connection_line_color")};'
                       f'stroke-width:{self.template.get_parameter_value("arrow_stroke_width")}"/>\n')
        self.svg.write('</marker>\n')

        # Reverse Arrow Head Style
        self.svg.write('\n<marker id="reverse_arrow_head" markerWidth="10" '
                       'markerHeight="7" refX="-3.5" refY="3.5" orient="auto">\n')
        self.svg.write('<polygon points="0 0, -10 3.5, 0 7"/>\n')
        self.svg.write('</marker>\n')

        # Open Arrow Head Style
        self.svg.write(
            '<marker id="open_arrow_head" markerWidth="10" markerHeight="11" refX="5" refY="5" orient="auto">\n')
        self.svg.write(f'<line x1="5" y1="5" x2="-3" y2="11" '
                       f'style="stroke:{self.template.get_parameter_value("connection_line_color")};'
                       f'stroke-width:{self.template.get_parameter_value("arrow_stroke_width")}"/>\n')
        self.svg.write(f'<line x1="-2" y1="-2" x2="5" y2="5" '
                       f'style="stroke:{self.template.get_parameter_value("connection_line_color")};'
                       f'stroke-width:{self.template.get_parameter_value("arrow_stroke_width")}"/>\n')
        self.svg.write('</marker>\n')
        self.svg.write('</defs>\n')

    def get_svg_string(self):
        svg_final = io.StringIO()

        self.add_title_to_svg()
        self.add_diagram_items_to_svg()
        self.svg.write('</svg>')

        svg_final.write(self.get_svg_header())
        svg_final.write(self.svg.getvalue())

        return svg_final.getvalue()

    def get_svg_header(self):
        svg_header = io.StringIO()
        svg_header.write('<svg version="1.2" xmlns="http://www.w3.org/2000/svg"'
                         ' xmlns:xlink="http://www.w3.org/1999/xlink" width="')
        svg_header.write(str(self.width))
        svg_header.write('" height="')
        svg_header.write(str(max(self.preferred_height, self.height)))
        svg_header.write('">\n')

        return svg_header.getvalue()

    def add_diagram_items_to_svg(self):
        task_id = 0
        connection_id = 0
        divider_id = 0
        note_id = 0
        graph_item_id = 0
        last_task_connection = None
        self.preferred_height = self.template.get_parameter_value('y_offset') + self.get_task_height() * 2
        for key in self.diagram.items:
            # If we are adding a task (or a the label of a lane)
            if isinstance(self.diagram.items[key], Task):
                self.add_task_to_svg(self.diagram.items[key], task_id)
                task_id += 1

            # If we are adding a connection (a horizontal arrow from a task to another)
            elif isinstance(self.diagram.items[key], TaskConnection):
                last_task_connection = self.diagram.items[key]
                self.add_connection_to_svg(self.diagram.items[key], graph_item_id, connection_id)
                connection_id += 1
                graph_item_id += 1

            # If we are adding divider (a horizontal separator with a title)
            elif isinstance(self.diagram.items[key], Divider):
                self.add_divider_to_svg(self.diagram.items[key], graph_item_id, divider_id)
                divider_id += 1
                graph_item_id += 1

            # If we are adding a note
            elif isinstance(self.diagram.items[key], Note):
                if self.diagram.items[key].start_task_id == -1 or self.diagram.items[key].end_task_id == -1:
                    self.add_note_to_svg(None, self.diagram.items[key], graph_item_id, note_id)
                else:
                    self.add_note_to_svg(last_task_connection, self.diagram.items[key], graph_item_id, note_id)
                note_id += 1
                graph_item_id += 1

        self.preferred_height += self.get_y_offset_for_graph_item(graph_item_id)
        if self.preferred_height > self.height:
            raise SVGSizeError(f"Diagram should have a height of at least"
                             f" {self.preferred_height} instead of {self.height}.")

    def add_note_to_svg(self, task_connection: TaskConnection, note: Note, graph_item_no: int, note_id: int):
        note_x, note_y, note_width, note_height = 0, 0, 0, 0

        if task_connection is None:
            note_x = self.get_mid_task_x(0) - self.template.get_parameter_value('arrow_height')
            note_width = self.get_mid_task_x(self.diagram.tasks_count - 1) \
                         + self.template.get_parameter_value('arrow_height') - note_x

        else:
            from_task_id = self.diagram.get_task_id(task_connection.source_task)
            to_task_id = self.diagram.get_task_id(task_connection.target_task)

            note_x = self.get_mid_task_x(from_task_id) - self.template.get_parameter_value('arrow_height')
            # Remove the amount of the distance between 2 tasks from note width
            note_width = self.get_mid_task_x(to_task_id) \
                         + self.template.get_parameter_value('arrow_height') - note_x

        note_y = self.get_y_offset_for_graph_item(graph_item_no) + self.template.get_parameter_value('arrow_height') * 2
        note_height = get_text_height(note.note_text
                                      , self.template.get_font_name_from_font_family_name('body-font-family')
                                      , self.template.get_parameter_value('body-font-size')
                                      , note_width)
        if debug:
            print(f'note_x={note_x}, note_y={note_y},note_width={note_width} and note_height={note_height}')

        self.svg.write(f'\n<!-- Note #{note_id + 1}, object #{graph_item_no + 1} -->\n')
        self.draw_box_with_text(f"note_{note_id + 1}"
                                , note.note_text
                                , self.template.get_parameter_value("body-font-size")
                                , note_x
                                , note_y
                                , note_width
                                , note_height
                                , fill_color='rgb(255, 253, 238)'
                                , stroke_color='rgb(221, 219, 204)'
                                , justification='left'
                                )

        self.graph_items_height[graph_item_no] = note_height + self.template.get_parameter_value('arrow_height') * 2

    def add_divider_to_svg(self, divider: Divider, graph_item_no: int, divider_id: int):
        self.svg.write(f'\n<!-- Divider #{divider_id}, object #{graph_item_no} -->\n')

        # The distance from the top of the graph is the offset until the previous graph item
        # divider_y = self.get_y_offset_for_graph_item(graph_item_no - 1)
        divider_y = self.get_y_offset_for_graph_item(graph_item_no)
        # print(f"divider_y_w is {divider_y_w}, while divider_y is {divider_y}.")

        if divider.style.lower() == 'delay':
            # Delay are shown wider on the graph to better represent a wait
            self.graph_items_height[graph_item_no] = self.template.get_parameter_value('space_between_connections') * 2
        else:
            self.graph_items_height[graph_item_no] = self.template.get_parameter_value('space_between_connections')

        # Divider spread the whole diagram, so we just skip the margin
        divider_x = self.get_x_offset(0)
        # The diagram width - left and right margins
        divider_to_x = self.width - 2 * self.template.get_parameter_value('x_offset')
        # The y coordinate for the end of the divider
        divider_to_y = divider_y + self.graph_items_height[graph_item_no]

        # Add Divider Text
        self.draw_box_with_text("divider", divider.label,
                                self.template.get_parameter_value("body-font-size"),
                                divider_x,
                                divider_y,
                                divider_to_x,
                                self.graph_items_height[graph_item_no],
                                fill_color='none',
                                stroke_color='none',
                                font_weight='bold'
                                )
        # Draw The Divider Line
        stroke, style = get_stroke_from_style_name(divider.style)
        if divider.style.lower() == 'delay':
            # Draw the delay divider. A white line to overwrite the background and make it look transparent
            for task_no in range(0, self.diagram.tasks_count):
                self.svg.write(f'<path id="delay_vertical_{graph_item_no}_{task_no}_back" d="M '
                               f'{self.get_mid_task_x(task_no)} {divider_to_y - self.graph_items_height[graph_item_no]} L'
                               f'{self.get_mid_task_x(task_no)} {divider_to_y}'
                               f'" stroke-width="4" fill="none" '
                               f'stroke="white" '  # TODO parametrize the background color
                               f'/>\n')
                # And a dashed line above the white line
                self.svg.write(f'<path id="delay_vertical_{graph_item_no}_{task_no}_front" d="M '
                               f'{self.get_mid_task_x(task_no)} {divider_to_y - self.graph_items_height[graph_item_no]} L'
                               f'{self.get_mid_task_x(task_no)} {divider_to_y}'
                               f'" stroke-width="{self.template.get_parameter_value("stroke_width")}" fill="none" '
                               f'stroke="{self.template.get_parameter_value("connection_line_color")}" '
                               f'stroke-dasharray=" 10 5"'
                               f'/>\n')
        else:
            self.svg.write(
                f'<path id="divider_line_{graph_item_no}" d="M {divider_x} '
                f'{divider_to_y} L {self.width - self.template.get_parameter_value("x_offset")} '
                f'{divider_to_y}" stroke="{self.template.get_parameter_value("connection_line_color")}" '
                f'stroke-width="{stroke}" fill="none" '
                f'{style}'
                f'/>\n')

    def add_task_to_svg(self, task: Task, task_no: int):
        """
        Draw the upper and lower tasks and the line connecting them
        :param task: the task to be drawn
        :param task_no: the id of the task
        :return:
        """
        self.svg.write(f'\n<!-- Task {task_no + 1} Node -->\n')
        y_offsets = [self.get_y_offset(), self.get_y_lower_node_offset()]
        for i in y_offsets:
            self.draw_box_with_text("task", task.description,
                                    self.template.get_parameter_value("body-font-size"),
                                    self.get_x_offset(task_no),
                                    i,
                                    self.get_task_width(),
                                    self.get_task_height(),
                                    box_corner=10,
                                    fill_color=self.template.get_parameter_value("task_fill_color"),
                                    stroke_color=self.template.get_parameter_value("task_line_color")
                                    )

        self.svg.write(f'<!-- Task {task_no + 1} Upper Lower Connector -->\n')
        self.svg.write(
            f'<path id="line_task_{task_no + 1}" d="M {self.get_mid_task_x(task_no)} '
            f'{self.get_task_upper_mid()} L {self.get_mid_task_x(task_no)} '
            f'{self.get_y_lower_node_offset()}" stroke="{self.template.get_parameter_value("connection_line_color")}" '
            f'stroke-width="{self.template.get_parameter_value("stroke_width")}" fill="none"/>\n')

    @lru_cache(maxsize=256)
    def get_mid_task_x(self, task_no: int):
        """
        Returns the point x where x is: (_Task__x__One_)
        :param task_no: The id of the task
        :return: the horizontal coordinate of the point in the middle of the task label
        """
        return self.get_x_offset(task_no) + int(self.get_task_width() / 2)

    @lru_cache(maxsize=2)
    def get_task_width(self):
        return int((self.width - self.template.get_parameter_value('x_offset')) / self.diagram.tasks_count) \
               - self.template.get_parameter_value('x_offset')

    @lru_cache(maxsize=256)
    def get_x_offset(self, task_no: int):
        return self.template.get_parameter_value('x_offset') + (
                (self.get_task_width() + self.template.get_parameter_value('x_offset')) * task_no)

    @lru_cache(maxsize=2)
    def get_task_upper_mid(self):
        return self.template.get_parameter_value('task_height') + self.get_y_offset()

    @lru_cache(maxsize=2)
    def get_y_offset(self):
        return self.template.get_parameter_value('y_offset')

    @lru_cache(maxsize=2)
    def get_task_height(self):
        return self.template.get_parameter_value('task_height')

    @lru_cache(maxsize=2)
    def get_y_lower_node_offset(self):
        return self.height - self.template.get_parameter_value(
            'stroke_width') - self.template.get_parameter_value('task_height')

    @lru_cache(maxsize=256)
    def get_y_offset_for_graph_item(self, graph_item_no: int):
        y_offset = 0
        for key in self.graph_items_height:
            if key <= graph_item_no:
                y_offset = y_offset + self.graph_items_height[key]

        if debug:
            print(f"For graph item #{graph_item_no}, the sum of the widths are {y_offset}.")
        return y_offset + self.get_task_height() + self.get_y_offset() + self.template.get_parameter_value(
            'arrow_height')

    @lru_cache(maxsize=256)
    def get_target_x_for_connection(self, to_task_id: int, lost_message=False):
        """
        Calculate where a connection should en
        :param to_task_id: The id of the task where the connection is going
        :param lost_message: Flag whether the connection should end with an arrow or not reach the task and end with 'x'
        :return: the horizontal coordinate of where the arrow should reach
        """
        if lost_message:
            return int(self.get_mid_task_x(to_task_id) * 0.9)
        else:
            return self.get_mid_task_x(to_task_id)

    @lru_cache(maxsize=2)
    def get_self_connection_height(self):
        return self.template.get_parameter_value('space_between_connections') - self.template.get_parameter_value(
            'arrow_height') * 2

    def add_connection_to_svg(self, task_connection: TaskConnection, graph_item_offset: int, connection_no: int):
        """
        Draws the arrow connecting two tasks. Was inspired by: http://thenewcode.com/1068/Making-Arrows-in-SVG to draw
        an arrow in SVG
        :param task_connection: the object holding the source and target of a connection between tasks
        :param graph_item_offset: The item offset in the graph starting from the top
        :param connection_no: which connection is it so far
        :return:
        """
        from_task_id = self.diagram.get_task_id(task_connection.source_task)
        to_task_id = self.diagram.get_task_id(task_connection.target_task)

        if from_task_id == to_task_id:
            to_self = True
            self.graph_items_height[graph_item_offset] = self.template.get_parameter_value('space_between_connections') * 2
        else:
            to_self = False
            self.graph_items_height[graph_item_offset] = self.template.get_parameter_value('space_between_connections')

        if from_task_id < 0 or to_task_id < 0:
            raise TypeError(f"Failed to find connection {connection_no}")

        self.svg.write(f'\n<!-- Connection {connection_no + 1} -->\n')
        stroke, style = get_stroke_from_style_name(task_connection.style)

        # arrow_y = self.get_y_offset_for_graph_item(graph_item_offset) \
        #           + self.template.get_parameter_value("space_between_connections")

        if to_self:
            # Now add the label associated to that swim lane
            text_y = self.get_y_offset_for_graph_item(graph_item_offset) \
                       - 2 * self.template.get_parameter_value('space_between_connections') \
                       + self.template.get_parameter_value('arrow_height')

            self.draw_box_with_text(f"self_connection_text_{connection_no + 1}", task_connection.label
                                    , self.template.get_parameter_value('body-font-size')
                                    , self.get_x_offset(from_task_id)
                                    , text_y
                                    , self.get_task_width()
                                    , self.template.get_parameter_value(
                    'space_between_connections') - self.template.get_parameter_value('arrow_height')
                                    , fill_color='white'
                                    , stroke_color='none')

            arrow_y_offset = self.get_y_offset_for_graph_item(graph_item_offset) \
                       - self.template.get_parameter_value('space_between_connections') \
                       + self.template.get_parameter_value('arrow_height')

            self.svg.write(
                f'<path id="self_connection_arrow_{connection_no + 1}" d="M {self.get_mid_task_x(from_task_id)} '
                f'{arrow_y_offset} L '
                f'{self.get_mid_task_x(from_task_id) + self.template.get_parameter_value("space_between_connections")} '
                f'{arrow_y_offset} L '
                f'{self.get_mid_task_x(from_task_id) + self.template.get_parameter_value("space_between_connections")} '
                f'{arrow_y_offset + self.get_self_connection_height()} '
                f'{self.get_mid_task_x(from_task_id)} '
                f'{arrow_y_offset + self.get_self_connection_height()} '
                f'" stroke="{self.template.get_parameter_value("connection_line_color")}" stroke-linejoin="round" ')
        else:
            # Now add the label associated to that swim lane
            self.draw_box_with_text("connection_text", task_connection.label,
                                    self.template.get_parameter_value('body-font-size')
                                    , min(self.get_mid_task_x(from_task_id),
                                          self.get_target_x_for_connection(to_task_id, task_connection.lost_message))
                                    , self.get_y_offset_for_graph_item(
                    graph_item_offset) - self.template.get_parameter_value('space_between_connections')
                                    , self.get_label_box_width(from_task_id, to_task_id, task_connection.lost_message)
                                    , self.template.get_parameter_value('space_between_connections')
                                    , fill_color='none'
                                    , stroke_color='none')
            self.svg.write(
                f'<path id="connection_arrow_{connection_no + 1}" d="M {self.get_mid_task_x(from_task_id)} '
                f'{self.get_y_offset_for_graph_item(graph_item_offset)} L '
                f'{self.get_target_x_for_connection(to_task_id, task_connection.lost_message)} '
                f'{self.get_y_offset_for_graph_item(graph_item_offset)}" '
                f'stroke="{self.template.get_parameter_value("connection_line_color")}" ')
        self.svg.write(f'stroke-width="{stroke}" fill="none" {style}')

        if task_connection.lost_message:
            self.svg.write(' marker-end="url(#lost_arrow_head)"')
        elif task_connection.open_arrow:
            self.svg.write(' marker-end="url(#open_arrow_head)"')
        else:
            self.svg.write(' marker-end="url(#arrow_head)"')

        if task_connection.bi_directional:
            self.svg.write(' marker-start="url(#reverse_arrow_head)"')
        self.svg.write('/>')

        # TODO re-calculate the this item's height

    def get_label_box_width(self, from_task_id: int, to_task_id: int, lost_message: bool):
        if from_task_id == to_task_id:
            return self.get_task_width()
        else:
            return abs(self.get_target_x_for_connection(to_task_id, lost_message) - self.get_mid_task_x(from_task_id))

    def add_title_to_svg(self):
        self.draw_box_with_text("title", self.diagram.title, self.template.get_parameter_value('title-font-size')
                                , 0, 0, self.width, self.template.get_parameter_value('y_offset')
                                , fill_color='none', stroke_color='none', font_family_param='title-font-family')

    def draw_box_with_text(self, box_name: str, text: str, font_size: int, box_x: int, box_y: int, box_width: int
                           , box_height: int, box_corner=0, fill_color='white', stroke_color='black'
                           , font_family_param='body-font-family',font_weight='normal', justification='center'):
        """
        Draw a box and render a text inside it. Handle text alignment and text wrapping
        :param font_family_param:
        :param box_name: a generic, one word without spaces ans special characters to help assign an id to the text box
        :param text: the text to be rendered in the box
        :param font_size: the size of the font to be rendered
        :param box_x: the x (horizontal) coordinate where the box should start
        :param box_y: the y (vertical) coordinate where the box should start
        :param box_width: the width of the text box
        :param box_height: the height of the text box
        :param box_corner: the rounding of the corner
        :param fill_color: the color to fill the rectangle
        :param stroke_color: the color of the line of the box. Use 'none' for no colors
        :param font_weight: either normal, bold, italic
        :param justification: either left or centered
        :return:
        """
        # Draw the box
        self.box_id += 1
        self.svg.write(
            f'<rect id="{box_name}_rectangle_{self.box_id}" x="{box_x}" y="{box_y}" rx="{box_corner}" ry="{box_corner}"'
            f' width="{box_width}" height="{box_height}" '
            f'style="fill:{fill_color};stroke:{stroke_color}'
            f';stroke-width:{self.template.get_parameter_value("stroke_width")}"/>\n')

        # Split the text into lines that fit in the box based on the font type and size
        lines = split_text(text, self.template.get_font_name_from_font_family_name('body-font-family')
                           , box_width, self.template.get_parameter_value('body-font-size'))

        if len(lines) < 1:
            return

        if lines[0][2] < 1:  # Use a logger and write a warning
            if debug:
                print(f"Text '{text}' was width {lines[0][1]} and height {lines[0][2]} "
                      f"in a rectangle of heigh {box_height} and width {box_width}.")
            return
        # How many lines of text can be displayed in the defined box?
        number_of_lines_that_can_be_printed = int(box_height / lines[0][2])

        margin_y = 0
        if len(lines) < number_of_lines_that_can_be_printed:
            #  Not enough lines to fill the box, let's shit the text by adding a margin
            margin_y = int((box_height - len(lines) * lines[0][2]) / 2)

        # Add the lines of text
        i = 1
        font_family = self.template.get_parameter_value(font_family_param)
        for line in lines:
            line_y = int(box_y + i * (self.template.get_parameter_value('body-font-size')) * 1.05) + margin_y
            if justification == 'center':
                line_x = int((abs(box_width - line[1])) / 2) + box_x  # Center the text
            else:
                line_x = box_x + self.template.get_parameter_value("stroke_width") * 2
            self.box_id += 1
            self.svg.write(
                f'<text id="{box_name}_text_{self.box_id}" x="{line_x}" y="{line_y}" '
                f'font-size="{font_size}" font-weight="{font_weight}" '
                f'font-family="{font_family}">'
                f'{line[0]}'
                f'</text>\n')
            i += 1
            if i > number_of_lines_that_can_be_printed:
                break
