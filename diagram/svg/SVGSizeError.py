from dataclasses import dataclass


@dataclass
class SVGSizeError(Exception):
    height: int
    width: int
    preferred_height: int
    preferred_width: int
