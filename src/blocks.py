from dataclasses import dataclass
from typing import Tuple
from enum import Enum, auto

@dataclass
class Chunk:
    name: str
    body: str
    info: str
    span: Tuple[int, int]

@dataclass
class Header:
    top_t: int
    bottom_t: int
    # TODO https://ru.wikipedia.org/wiki/Темп_(музыка)
    bpm: int
    volume: int
    pitch: int
    octave: int

class NoteModifier(Enum):
    NONE = auto()
    SHARP = auto()
    FLAT = auto()

@dataclass
class Note:
    name: str
    duration: float
    line: int
    modifier: NoteModifier

@dataclass
class Variable[T]:
    name: str
    value: T

@dataclass
class Pair:
    left: str
    right: str