from math import sin, pi
from array import array
from blocks import Note, NoteModifier, Header
from typing import List

def note(start, step):
    return start * (2 ** (step / 12))

def scale(start):
    progress = 0, 2, 2, 1, 2, 2, 2, 1
    idx = 0
    for i in progress:
        idx += i
        yield note(start, idx)

def clamp_volume(volume):
    if volume < 0:
        volume = 0
    if volume > 1:
        volume = 1
    return volume

class Percentage:
    def __init__(self: int, p) -> float:
        self.p = p
    
    def of(self, other):
        return self.p / 100 * other

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
    hz = (frequency * 2 * pi) / samplerate
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

second = 48_000

def reverse_wave(n):
    return [*map(lambda x: x * -1, n)]


def join_waves(left, right):
    if left[-1] < 0:
        return reverse_wave(right)
    return right

def run():
    sound = []
    previous = None
    notes = 261.626,
    bpm = 60/60
    for note_ in notes:
        for n in scale(note_):
            if previous:
                sound.extend(join_waves(previous, wave(bpm * 0.5, n, 1)))
            else:
                previous = wave(bpm, n, 0.5)
                sound.extend(previous)
    out = 'hello.bin'
    with open(out, 'wb') as output:
        audio = array('d', sound)
        audio.tofile(output)

# nuh huh
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
    if distance >= 0:
        new_octave = hz * distance * 2 or hz
    else:
        new_octave = hz / (distance * 2)
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