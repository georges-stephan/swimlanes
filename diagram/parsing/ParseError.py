from dataclasses import dataclass


@dataclass
class ParsingError(Exception):
    line_number: int
    note_boundaries: str


@dataclass
class ParsingUnknownStateError(Exception):
    state_number: int
