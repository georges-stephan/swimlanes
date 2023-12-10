import platform
from abc import ABC, abstractmethod

from diagram.components.StyleError import StyleError


class Template(ABC):

    def __init__(self, parameters_dict):
        self.parameters_dict = parameters_dict

    @abstractmethod
    def get_parameter_value(self, parameter_name: str) -> int | str:
        pass

    def get_font_name_from_font_family_name(self, template_parameter_font_family) -> str:
        if self.get_parameter_value(template_parameter_font_family) is None:
            raise StyleError(f'Unknown template parameter {template_parameter_font_family}')

        if self.get_parameter_value(template_parameter_font_family).strip().lower() == 'sans-serif':
            if platform.system() == 'Windows':
                return 'arial'
            else:
                # TODO also check if we are running on Linux or Mac
                # TODO check is liberation fonts are installed
                return 'liberation-sans'
        else:
            # Assuming Serif Font
            if platform.system() == 'Windows':
                return 'times'
            else:
                # TODO also check if we are running on Linux or Mac
                return 'liberation-serif'
