from dataclasses import dataclass


@dataclass
class RenderingConnectionError(Exception):
    connection_no: int


@dataclass
class RenderingStyleError(Exception):
    style_name: str
