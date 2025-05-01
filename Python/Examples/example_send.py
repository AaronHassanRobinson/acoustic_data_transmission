# simple_send_loop_startstop.py
import numpy as np
import sounddevice as sd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Acoustic import *

# using constants defined in constants.y in acoustic module
# can redefine these if not fit for purpose

# eventual packet goal
# [preamble][start_bit][packet_header][message][stop_bit]a

def send_message(message):
    bits = PREAMBLE + []

    for char in message:
        bits.append('start')
        bits.extend([int(b) for b in format(ord(char), '08b')])
        bits.append('stop')
        bits.append('silence')  # used for timing alignment 

    signal = []
    for bit in bits:
        if bit == 'start':
            signal.append(generate_tone(FREQ_START))
        elif bit == 'stop':
            signal.append(generate_tone(FREQ_STOP))
        elif bit == 'silence':
            signal.append(np.zeros(int(SAMPLE_RATE * (DURATION * 0.5))))  # Half a bit of silence
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