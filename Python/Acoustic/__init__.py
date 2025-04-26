# python/acoustic/__init__.py

"""
Acoustic Communication Stack
===============================

This package provides the core functionality for acoustic data transmission with an underwater drone, however can also be adapted for any
wireless communication.
including:
FSK modulation,
protocol handling,
sound I/O,
bit packing / serialization,  
It abstracts
underwater acoustic networking into usable components for simulations or
real-world interfacing.

Modules:
--------
- fsk            : FSK modulation/demodulation logic
- protocol       : Bit framing, preamble detection, CRC
- physical       : Audio interface for playback/recording
- codec          : Bit-packing, serialization/deserialization
- signal_filters : Signal filtering functions
"""

from .fsk import modulate_fsk, demodulate_fsk
from .protocol import encode_packet, decode_packet, detect_preamble
from .physical import record_audio, play_audio
from .codec import pack_bits, unpack_bits
from .signal_filters import butter_bandpass, bandpass_filter

__all__ = [
    "modulate_fsk",
    "demodulate_fsk",
    "encode_packet",
    "decode_packet",
    "detect_preamble",
    "record_audio",
    "play_audio",
    "pack_bits",
    "unpack_bits",
    "butter_bandpass",
    "bandpass_filter"
]