from templates.Template import Template
import platform


class DefaultTemplate(Template):

    def __init__(self):
        self.parameters_dict = {
            'x_offset': 50,
            'y_offset': 70,
            'task_width': 150,
            'task_height': 50,
            'stroke_width': 2,
            'task_line_color': 'grey',
            'task_fill_color': 'white',
            'space_between_connections': 50,
            'connection_line_color': 'black',
            'arrow_height': 10,
            'title-font-family': 'sans-serif',
            'title-font-size': 16,
            'body-font-family': 'sans-serif',
            'body-font-size': 14,
            'arrow_stroke_width': 1,
            'text_margin-top': 4,
            'text_margin-bottom': 4,
            'text_margin-left': 4,
            'text_margin-right': 4
        }

    def get_parameter_value(self, parameter_name: str):
        return self.parameters_dict[parameter_name]

    def get_font_name_from_font_family_name(self, font_family_name):
        if self.parameters_dict[font_family_name] is None:
            raise TypeError(f'Unknown font family {font_family_name}')

        if self.parameters_dict[font_family_name] == 'sans-serif':
            if platform.system() == 'Windows':
                return 'arial'
            else:
                # TODO also check if we are running on Linux or Mac
                return 'liberation-sans'
        else:
            # Assuming Serif Font
            if platform.system() == 'Windows':
                return 'times'
            else:
                # TODO also check if we are running on Linux or Mac
                return 'liberation-serif'
