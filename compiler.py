from typing import Tuple, Generator, Any
from dataclasses import dataclass
from string import ascii_letters

_PITCHDEFAULT = 430

@dataclass
class Header:
    top_t: int
    bottom_t: int
    bpm: int
    pitch: int


@dataclass
class Note:
    name: str
    duration: float
    line: int


@dataclass
class Chunk:
    name: str
    body: str
    info: str

    def __repr__(self):
        return f"Chunk {self.name}:\n\tByteCode:\n{self.info}\n{self.body}\nend"

def _is_ident(c) -> bool:
    return c in ascii_letters or c == '_'

class Lexer:
    def __init__(self, input: str) -> None:
        self.input: str = input
        self._len: int = len(input)
        self._cursor: int = 0
        self._line: int = 0

    def _has(self) -> bool:
        return self._cursor < self._len
    
    def _parse_ws(self) -> None:
        while self._has() and self.input[self._cursor] == ' ':
            self._cursor += 1

    def _parse_integer(self) -> int:
        self._parse_many_nl()
        out = ''
        while self._has() and self.input[self._cursor].isnumeric():
            out += self.input[self._cursor]
            self._cursor += 1
        if not out:
            raise SyntaxError(f"{self._cursor}: Expected an integer")
        return int(out)

    def _parse_symbol(self, symbol: str) -> None:
        self._parse_many_nl()
        if self._has() and self.input[self._cursor:self._cursor + (l := len(symbol))] == symbol:
            self._cursor += l
            return
        raise SyntaxError(f"Expected symbol '{symbol}'")

    def _parse_fraction(self) -> Tuple[int, int]:
        left = self._parse_integer()
        self._parse_symbol('/')
        right = self._parse_integer()
        return left, right
    
    def _parse_key_value_int(self, key: str) -> int:
        self._parse_symbol(key)
        self._parse_symbol(":")
        val = self._parse_integer()
        self._parse_nl_strict()
        return val
    
    def _parse_nl_strict(self) -> None:
        if self._has() and self.input[self._cursor] not in '\n;':
            raise SyntaxError(f"{self._line}: {self._cursor} :Expected new line")
        self._cursor += 1
        self._line += 1
    
    def _parse_many_nl(self) -> None:
        self._parse_ws()
        while self._has() and self.input[self._cursor] == '\n':
            self._cursor += 1
            self._line += 1

    def parse_header(self) -> Header:
        time_signature_top, time_signature_bottom = self._parse_fraction()
        self._parse_nl_strict()
        bpm = self._parse_key_value_int('bpm')
        pitch: int = self._try_to(lambda: self._parse_key_value_int('pitch')) or _PITCHDEFAULT
        return Header(time_signature_top, time_signature_bottom, bpm, pitch)

    def _parse_ident(self) -> str:
        self._parse_many_nl()
        out = ''
        while self._has() and _is_ident(self.input[self._cursor]):
            out += self.input[self._cursor]
            self._cursor += 1
        if not out:
            raise SyntaxError(f"{self._cursor}: Expected identifier")
        return out

    def _parse_label(self) -> str:
        self._parse_symbol('@')
        name = self._parse_ident()
        self._parse_nl_strict()
        return name

    def _parse_key_value_int_any(self) -> Tuple[str, int]:
        ident = self._parse_ident()
        self._cursor -= len(ident)
        value = self._parse_key_value_int(ident)
        self._cursor -= 1
        return ident, value

    def _parse_note(self) -> Note:
        if (name:=self.input[self._cursor]) in "ABCDEFG":
            self._cursor += 1
            self._parse_ws()
            dur = self._parse_integer()
            self._parse_nl_strict()
            self._cursor -= 1 # don't change, on purpose.
            return Note(name, dur, self._line)
        raise SyntaxError(f"{self._cursor}: Not a note!")

    def _parse_goto_like(self) -> Tuple[str, str]:
        left = self._parse_ident()
        right = self._parse_ident()
        self._parse_nl_strict()
        return left, right
        
    def _try_to(self, func) -> Any:
        prevc = self._cursor
        prevl = self._line
        res = None
        try:
            res = func()
        except:
            self._cursor = prevc
            self._line = prevl
        return res

    def _parse_elements(self) -> Generator[Note | Any, None, None]:
        order = self._parse_key_value_int_any, self._parse_note, self._parse_goto_like
        for f in order:
            while (ret := self._try_to(f)) != None:
                yield ret

    def _get_chunk(self) -> Chunk:
        name = self._parse_label()
        body = ''
        notes = []
        while self._has() and self.input[self._cursor] != '@':
            b = [*self._parse_elements()]
            if b:
                notes.append(b)
            # ; is skipped
            if self._has() and self.input[self._cursor] not in ';\n':
                    body += self.input[self._cursor]
            self._cursor += 1
        return Chunk(name, body, notes)

    def parse_program(self):
        while self._has():
            print(self._get_chunk())
        print(self._line)

    def parse(self):
        print(self.parse_header())
        self.parse_program()


@dataclass
class Interpreter:
    header: Header
    chunks: Tuple[Chunk]