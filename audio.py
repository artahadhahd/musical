from math import sin, pi
from array import array

def note(start, step):
    return start * (2 ** (step / 12))

def scale(start):
    progress = [0, 2, 2, 1, 2, 2, 2, 1]
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
    return [clamp_volume(volume) * sin(i * hz) for i in range(int(samplerate * duration))]

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
    bpm = 60/420
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

import sys
run()

# try:
#     run()
# except Exception as e:
#     run()
#     sys.exit(1)