from dataclasses import dataclass


@dataclass
class SVGSizeError(Exception):
    height: int
    preferred_height: int
