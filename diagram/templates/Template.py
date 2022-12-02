import platform
from abc import ABC, abstractmethod


class Template(ABC):

    def __init__(self, parameters_dict):
        self.parameters_dict = parameters_dict

    @abstractmethod
    def get_parameter_value(self, parameter_name: str) -> int | str:
        pass

    def get_font_name_from_font_family_name(self, font_family_name) -> str:
        if self.parameters_dict[font_family_name] is None:
            raise TypeError(f'Unknown font family {font_family_name}')

        if self.parameters_dict[font_family_name].strip().lower() == 'sans-serif':
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
