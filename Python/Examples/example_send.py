# simple_send_loop_startstop.py
import numpy as np
import sounddevice as sd

# Configuration
SAMPLE_RATE = 44100
DURATION = 0.1  # seconds per bit
FREQ0 = 16000
FREQ1 = 17000
FREQ_START = 15500
FREQ_STOP = 17500
PREAMBLE = [1,0,1,0,1,0,1,0]

def text_to_bits(text):
    bits = []
    for char in text:
        bits.extend(int(b) for b in format(ord(char), '08b'))
    return bits

def generate_tone(freq):
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t)
    return wave

def send_message(message):
    bits = PREAMBLE + []

    for char in message:
        bits.append('start')  # Special start marker
        bits.extend([int(b) for b in format(ord(char), '08b')])
        bits.append('stop')   # Special stop marker

    signal = []
    for bit in bits:
        if bit == 'start':
            signal.append(generate_tone(FREQ_START))
        elif bit == 'stop':
            signal.append(generate_tone(FREQ_STOP))
        else:
            freq = FREQ1 if bit else FREQ0
            signal.append(generate_tone(freq))
    signal = np.concatenate(signal)

    sd.play(signal, samplerate=SAMPLE_RATE)
    sd.wait()

def main():
    print("FSK Sender with start/stop bits Ready. Type text and press ENTER to send.")
    while True:
        try:
            text = input("> ")
            if text.strip() == "":
                continue
            send_message(text)
            print(f"Sent: '{text}'")
        except KeyboardInterrupt:
            print("\nExiting sender...")
            break

if __name__ == "__main__":
    main()