from dataclasses import dataclass


@dataclass
class StyleError(Exception):
    message: str
