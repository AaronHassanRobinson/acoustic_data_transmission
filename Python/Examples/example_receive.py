# simple_receive_loop_startstop.py
import numpy as np
import sounddevice as sd

# Configuration
SAMPLE_RATE = 44100
DURATION = 0.1  # seconds per bit
FREQ0 = 16000
FREQ1 = 17000
FREQ_START = 15500
FREQ_STOP = 17500
THRESHOLD = 0.01
PREAMBLE = [1,0,1,0,1,0,1,0]

def bits_to_text(bitgroups):
    chars = []
    for bits in bitgroups:
        byte = bits
        if len(byte) == 8:
            chars.append(chr(int(''.join(map(str, byte)), 2)))
    return ''.join(chars)

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

def find_preamble(bits):
    preamble_str = ''.join(map(str, PREAMBLE))
    bits_str = ''.join(map(str, bits))
    index = bits_str.find(preamble_str)
    return index if index != -1 else None

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
                    idx = find_preamble(bits)
                    if idx is not None:
                        bits = symbols[idx + len(PREAMBLE):]
                        
                        # Now parse chars by start/stop wrapping
                        messages = []
                        current_byte = []
                        collecting = False

                        for sym in bits:
                            if sym == 'start':
                                collecting = True
                                current_byte = []
                            elif sym == 'stop':
                                if collecting:
                                    messages.append(current_byte)
                                    collecting = False
                            elif collecting and isinstance(sym, int):
                                current_byte.append(sym)

                        text = bits_to_text(messages)
                        print(f"Received: '{text}'")
                    else:
                        print("Preamble not found.")

                    recording = False
                    buffer = []

    except KeyboardInterrupt:
        print("\nExiting receiver...")
        stream.stop()

if __name__ == "__main__":
    main()