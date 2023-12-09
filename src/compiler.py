from typing import Tuple, Generator, Any
from string import ascii_letters
from blocks import Variable, Chunk, Header, Pair, Note, NoteModifier
from math import log2
import audio

_PITCHDEFAULT = 430
_VOLUMEDEFAULT = 50
_OCTAVEDEFAULT = 4


class Interpreter:
    def __init__(self, header: Header, chunks: Tuple[Chunk]):
        self.header: Header = header
        self.chunks: Tuple[Chunk] = chunks
        self._chunk_pool: dict[str, Chunk] = {}
        self.variable_pool: dict[str, Variable[int]] = {}
        self.setup()
        self.current_chunk = self._chunk_pool['main']
        self.audio_system = audio.AudioSystem(header)

    class Error(Exception):
        pass

    def check_for_chunk_errors(self):
        for chunk in self.chunks:
            if chunk.body:
                raise self.Error(f"@{chunk.name}{chunk.span}: unexpected '{chunk.body}'")
            self._chunk_pool[chunk.name] = chunk
        if 'main' not in self._chunk_pool:
            raise self.Error(f"@main is missing")
    
    def clamp_volume(self):
        if self.header.volume < 0:
            print('warning: volume under 0, clamping to 0')
            self.header.volume = 0
        if self.header.volume > 100:
            print('warning: volume above 100, clamping to 100')
            self.header.volume = 100
    
    def check_time_signature(self):
        is_to_power = log2(self.header.bottom_t)
        if is_to_power - int(is_to_power) != 0:
            raise self.Error(f"Time signature's bottom value should be a power of 2, got '{self.header.bottom_t}' instead")
        
    def check_pitch(self):
        if self.header.pitch <= 0:
            raise self.Error("Pitch has to be above 0")

    def setup(self):
        self.check_for_chunk_errors()
        self.clamp_volume()
        self.check_time_signature()
        self.check_pitch()
    
    def goto(self, label):
        try:
            self.run_chunk(label)
        except RecursionError:
            raise self.Error('hit max limit for recursion')

    def interpret_pair(self, pair: Pair):
        match pair.left:
            case 'goto':
                self.goto(pair.right)
            case 'save':
                self.audio_system.save(pair.right)
            case _:
                raise self.Error(f'Invalid pair {pair}')
    
    def update_variable_pool(self, var: Variable[int]):
        match var.name:
            case 'octave' | 'bpm' | 'pitch' | 'volume' | 'meter':
                # getattr(self.header, var.name) = var.value
                setattr(self.header, var.name, var.value)
                self.audio_system.update_headers(self.header)
            case _:
                self.variable_pool[var.name] = var
    
    def run_chunk(self, chunk_name: str):
        if chunk_name not in self._chunk_pool:
            raise self.Error(f"@{chunk_name} doesn't exist")
        for info in self._chunk_pool[chunk_name].info:
            for op in info:
                match op:
                    case Pair() as pair:
                        self.interpret_pair(pair)
                    case Note() as note:
                        self.audio_system.add_sound(note)
                    case Variable() as var:
                        self.update_variable_pool(var)
                    case _ as op_:
                        raise self.Error(f'Unknown op {op_}')

    def run(self):
        self.run_chunk('main')

def _is_ident(c) -> bool:
    return c in ascii_letters or c in '_.'

class Parser:
    class Error(Exception):
        pass

    def __init__(self, input: str) -> None:
        self.input: str = input
        self._len: int = len(input)
        self._cursor: int = 0
        self._line: int = 0

    def parse_header(self) -> Header:
        time_signature_top, time_signature_bottom = self._parse_key_value_frac('meter')
        self._parse_nl_strict()
        bpm = self._parse_key_value_int('bpm')
        pitch: int = self._try_to(lambda: self._parse_key_value_int('pitch')) or _PITCHDEFAULT
        volume: int = self._try_to(lambda: self._parse_key_value_int('volume')) or _VOLUMEDEFAULT
        octave: int = self._try_to(lambda: self._parse_key_value_int('octave')) or _OCTAVEDEFAULT
        return Header(time_signature_top, time_signature_bottom, bpm, volume, pitch, octave)

    def parse_program(self) -> Generator[Chunk, None, None]:
        while self._has():
            yield self._get_chunk()

    def parse(self) -> Interpreter:
        header = self.parse_header()
        program = [*self.parse_program()]
        return Interpreter(header, program)

    def _has(self) -> bool:
        return self._cursor < self._len
    
    def _parse_key_value_frac(self, key: str):
        self._parse_symbol(key)
        self._parse_symbol(':')
        out = self._parse_fraction()
        return out
    
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
            raise self.Error(f"{self._cursor}: Expected an integer")
        return int(out)

    def _parse_symbol(self, symbol: str) -> None:
        self._parse_many_nl()
        if self._has() and self.input[self._cursor:self._cursor + (l := len(symbol))] == symbol:
            self._cursor += l
            return True
        raise self.Error(f"Expected symbol '{symbol}'")

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
            raise self.Error(f"{self._line}: {self._cursor} :Expected new line")
        self._cursor += 1
        self._line += 1
    
    def _parse_many_nl(self) -> None:
        self._parse_ws()
        while self._has() and self.input[self._cursor] == '\n':
            self._cursor += 1
            self._line += 1

    def _parse_ident(self) -> str:
        self._parse_many_nl()
        out = ''
        while self._has() and _is_ident(self.input[self._cursor]):
            out += self.input[self._cursor]
            self._cursor += 1
        if not out:
            raise self.Error(f"{self._cursor}: Expected identifier")
        return out

    def _parse_label(self) -> str:
        self._parse_symbol('@')
        name = self._parse_ident()
        self._parse_nl_strict()
        return name

    def _parse_key_value_int_any(self) -> Variable[int]:
        ident = self._parse_ident()
        self._cursor -= len(ident)
        value = self._parse_key_value_int(ident)
        self._cursor -= 1
        return Variable(ident, value)
    
    def _parse_int_fraction(self) -> int | Tuple[int, int]:
        frac = self._try_to(self._parse_fraction)
        if frac is not None:
            return frac[0] / frac[1]
        return self._parse_integer()
    
    def _parse_note(self) -> Note:
        if (name:=self.input[self._cursor]) in "ABCDEFG":
            self._cursor += 1
            self._parse_ws()
            modifier = NoteModifier.NONE
            dur = self._try_to(self._parse_int_fraction)
            if dur is None:
                if self._try_to(lambda: self._parse_symbol('#')):
                    modifier = NoteModifier.SHARP
                elif self._try_to(lambda: self._parse_symbol('b')):
                    modifier = NoteModifier.FLAT
                dur = self._parse_int_fraction()
            self._parse_many_nl()
            self._cursor -= 1 # don't change, on purpose.
            return Note(name, dur, self._line, modifier) 
        raise self.Error(f"{self._cursor}: Not a note!")

    def _parse_goto_like(self) -> Pair:
        left = self._parse_ident()
        right = self._parse_ident()
        # self()
        return Pair(left, right)
        
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
        start = self._line
        while self._has() and self.input[self._cursor] != '@':
            b = [*self._parse_elements()]
            if b:
                notes.append(b)
            # ; is skipped
            if self._has() and self.input[self._cursor] != '\n':
                body += self.input[self._cursor]
            self._cursor += 1
        return Chunk(name, body, notes, (start, self._line))
