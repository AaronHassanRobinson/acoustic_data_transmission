# simple_receive_loop_startstop.py
import numpy as np
import sounddevice as sd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Acoustic import *

# using constants defined in constants.y in acoustic module
# can redefine these if not fit for purpose

def detect_symbol(chunk):
    window = np.hanning(len(chunk))
    chunk = chunk * window
    fft = np.fft.fft(chunk)
    magnitudes = np.abs(fft)

    n = len(chunk)
    freq_bins = np.fft.fftfreq(n, 1/SAMPLE_RATE)

    def get_energy(target_freq):
        idx = np.argmin(np.abs(freq_bins - target_freq))
        return magnitudes[idx]

    energy0 = get_energy(FREQ0)
    energy1 = get_energy(FREQ1)
    energy_start = get_energy(FREQ_START)
    energy_stop = get_energy(FREQ_STOP)

    energies = {
        'start': energy_start,
        'stop': energy_stop,
        0: energy0,
        1: energy1,
    }

    detected = max(energies, key=energies.get)
    if energies[detected] < 5.0:
        return None

    return detected



def main():
    print("FSK Receiver with start/stop bits Ready. Listening... Press Ctrl+C to stop.")
    blocksize = int(SAMPLE_RATE * DURATION)

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=blocksize)
    stream.start()

    buffer = []
    recording = False

    try:
        while True:
            block, _ = stream.read(blocksize)
            block = block[:, 0]
            energy = np.sum(block ** 2) / len(block)

            if not recording:
                if energy > THRESHOLD:
                    print("Signal detected, recording message...")
                    recording = True
                    buffer = list(block)
            else:
                buffer.extend(block)

                if len(buffer) >= blocksize * (len(PREAMBLE) + (10 * 10)):  # Enough for small message
                    samples_per_bit = int(SAMPLE_RATE * DURATION)
                    symbols = []
                    for i in range(0, len(buffer), samples_per_bit):
                        chunk = buffer[i:i+samples_per_bit]
                        if len(chunk) < samples_per_bit:
                            break
                        symbol = detect_symbol(chunk)
                        if symbol is not None:
                            symbols.append(symbol)

                    # Separate preamble
                    bits = [s for s in symbols if isinstance(s, int)]
                    idx = detect_preamble(bits, PREAMBLE=PREAMBLE)
                    if idx is not None:
                        bits = symbols[idx + len(PREAMBLE):]
                        
                        # Now parse chars by start/stop wrapping
                        current_byte = []
                        collecting = False

                        for sym in bits:
                            if sym == 'start':
                                collecting = True
                                current_byte = []
                            elif sym == 'stop':
                                if collecting:
                                    # We finished a byte, decode and print it
                                    byte_text = unpack_bits([current_byte])
                                    print(f"Received byte: '{byte_text}'")
                                    collecting = False

                            elif collecting and isinstance(sym, int):
                                current_byte.append(sym)
                    else:
                        print("Preamble not found.")
                    recording = False
                    buffer = []

    except KeyboardInterrupt:
        print("\nExiting receiver...")
        stream.stop()

if __name__ == "__main__":
    main()