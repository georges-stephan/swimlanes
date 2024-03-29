import json
from abc import ABC
import logging
from json import JSONDecodeError

from diagram.templates.Template import Template

logger = logging.getLogger(__name__)


class FileTemplate(Template, ABC):
    __slots__ = "json_file_name"

    def __init__(self, json_file_name: str):
        with open(json_file_name, 'r') as f:
            try:
                self.template = json.load(f)
            except JSONDecodeError as e:
                logger.error(f"Template file {json_file_name} is corrupted:{e.msg}")
            except FileNotFoundError as e:
                logger.error(f"Config file {json_file_name} was not found:{e.filename}")

    def get_parameter_value(self, parameter_name: str) -> int | str:
        return self.template[parameter_name]
