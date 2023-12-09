from math import sin, tau
from array import array
from blocks import Note, NoteModifier, Header
from typing import List, Iterable


def note(start: float, step: int) -> float:
    """
    Returns a note `step` semitones away from `start`.
    So if start is `C`, and step is `1`, the output
    would be C# (C sharp). Similarly, if step is `-1`,
    then it would be a B (or a Cb [C flat] which is a same as
    a B)
    """
    return start * (2 ** (step / 12))

def major_scale(start):
    # These are the semitones that have to go up for a major scale
    # You can create any kind of scale by modifying these values
    progress = 0, 2, 2, 1, 2, 2, 2, 1
    idx = 0
    for i in progress:
        idx += i
        yield note(start, idx)


# IGNORE
class Percentage:
    def __init__(self: int, p) -> float:
        self.p = p
    
    def of(self, other):
        return self.p / 100 * other

# IGNORE, i will use it later but i don't wanna remove it
def adsr(input_: int, a: Percentage, d: Percentage, s: Percentage, r: Percentage, duration: float, samplerate=48e3):
    stage = a.of(samplerate)
    offset = 5000
    if input_ < stage * duration:
        return input_ / offset
    stage += d.of(samplerate)
    last = 0
    if input_ < stage:
        input_ = samplerate - input_
        last = input_
        return input_ / (offset * 10)
    stage += s.of(samplerate)
    if input_ < stage:
        return last
    stage += r.of(samplerate)
    if input_ <= stage:
        input_ = samplerate - input_
        return input_ / (offset * 4)
    raise RuntimeError(f'samplerate too much {input_}')


def wave(duration, frequency, volume, samplerate=48e3):
    hz = (frequency * tau) / samplerate
    volume /= 100
    return [volume * sin(i * hz) for i in range(int(samplerate * duration))]
    out = []
    # def estimate_ADSR(v: int) -> int:
    #     # if amplitude is below one / upto of the whole wave
    #     upto = 2
    #     if v < samplerate * duration / upto:
    #         return v / 100000
    #     v = samplerate * duration - v
    #     return v / 100000

    for i in range(int(samplerate * duration)):
        # v = estimate_ADSR(i % (samplerate * duration))
        v = adsr(i, Percentage(10), Percentage(20), Percentage(40), Percentage(30), duration, samplerate * duration)
        out.append(v * sin(i * hz))
    return out

def reverse_wave(n: Iterable[float]):
    return [-x for x in n]


def join_waves(left, right):
    if left[-1] < 0:
        return reverse_wave(right)
    return right

to_order = {
    'A' : 0,
    'B' : 2,
    'C' : -9,
    'D' : -7,
    'E' : -5,
    'F' : -4,
    'G' : -2,
}

modtoint = {
    NoteModifier.FLAT : -1,
    NoteModifier.NONE : 0,
    NoteModifier.SHARP : 1,
}

def note_from(note_: Note, hz: int, octave: int, base_octave: int = 4):
    distance = octave - base_octave
    new_octave = hz * distance * 2 or hz if distance >= 0 else hz / (distance * 2)
    return note(new_octave, to_order[note_.name] + modtoint[note_.modifier])

class AudioSystem:
    def __init__(self, header: Header):
        self.meta: Header = header
        self.sounds: List[float] = []

    def add_sound(self, note_: Note):
        new_note = note_from(note_, self.meta.pitch, self.meta.octave)
        self.sounds.extend(wave(note_.duration / (self.meta.bpm / 60), new_note, self.meta.volume))
        
    def update_headers(self, header: Header):
        self.meta = header
        
    def save(self, file: str):
        with open(file, 'wb') as output:
            audio = array('d', self.sounds)
            audio.tofile(output)
