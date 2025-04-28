import numpy as np
import sounddevice as sd
from .constants import *


def record_audio():
    pass

def play_audio():
    pass

def generate_tone(freq):
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t)
    return wave