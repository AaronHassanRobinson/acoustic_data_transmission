import numpy as np
import sounddevice as sd
import time
"""
Test send a char byte to a listening client acoustically
===============================
By Aaron Hassan Robinson
This code contains functions to send a byte, (hard set to 'K') to a listening client via acoustic signals. 
All frequencies in Hz: 
FREQ_START: The start bit, tells client to begin receiving
FREQ_STOP: Stop bit, tells client transmission has ended
FREQ_0: 0 Bit
FREQ_1: 1 Bit
// -- // -- //
BIT_DURATION: How long to play each tone for, the user should synchronize this with the receiving client
"""



# Protocol frequencies
FREQ_START = 200
FREQ_STOP = 1000
FREQ_0 = 500
FREQ_1 = 700

# Transmission settings
SAMPLE_RATE = 44100      # Standard audio sample rate
BIT_DURATION = 0.5    

def generate_tone(frequency, duration=BIT_DURATION, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t)  # amplitude 0.5
    return waveform.astype(np.float32)

def send_byte(byte_val):
    tones = []

    # Start bit
    tones.append(generate_tone(FREQ_START))

    # Data bits (MSB first)
    for i in range(7, -1, -1):
        bit = (byte_val >> i) & 1
        tones.append(generate_tone(FREQ_1 if bit else FREQ_0))

    # Stop bit
    tones.append(generate_tone(FREQ_STOP))

    # Concatenate and play
    signal = np.concatenate(tones)
    sd.play(signal, samplerate=SAMPLE_RATE)
    sd.wait()

if __name__ == "__main__":
    byte_to_send = ord('K')  # 0b01001011
    print(f"Sending byte: '{chr(byte_to_send)}' ({byte_to_send:#010b})")
    send_byte(byte_to_send)