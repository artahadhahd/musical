from math import sin, pi
from array import array
from dataclasses import dataclass
from blocks import *
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

def wave(duration, frequency, volume, samplerate=48e3):
    hz = (frequency * 2 * pi) / samplerate
    # volume /= 100
    # return [volume * sin(i * hz) for i in range(int(samplerate * duration))]
    out = []
    def estimate_ADSR(v: int) -> int:
        if v < (samplerate * duration) / (10 * duration):
            v /= volume * 100
        elif v > (samplerate * duration) / (90 * duration):
            v = samplerate - v
            v = v / samplerate * duration
        else:
            v = volume / 100
        return v
    for i in range(int(samplerate * duration)):
        v = estimate_ADSR(i % samplerate)
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
    # left = wave(0.5, 1, 1)
    # sound.extend(left)
    # right = wave(0.5, 1, 1)
    # sound.extend(join_waves(left, right))
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

class AudioSystem:
    def __init__(self, header: Header):
        self.meta: Header = header
        self.sounds: List[float] = []

    def add_sound(self, note_: Note):
        a_base = 4
        distance = self.meta.octave - a_base
        if distance >= 0:
            new_octave = self.meta.pitch * distance * 2 or self.meta.pitch
        else:
            new_octave = self.meta.pitch / (distance * 2)
        new_note = note(new_octave, to_order[note_.name] + modtoint[note_.modifier])
        self.sounds.extend(wave(note_.duration, new_note, self.meta.volume))
    
    def update_headers(self, header: Header):
        self.meta = header
        
    def save(self, file: str):
        with open(file, 'wb') as output:
            audio = array('d', self.sounds)
            audio.tofile(output)