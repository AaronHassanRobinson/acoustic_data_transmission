# example_send.py

import argparse
import sounddevice as sd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Acoustic import modulate_fsk

# Configuration
SAMPLE_RATE = 44100
DEFAULT_FREQ0 = 18000  # Hz (0-bit)
DEFAULT_FREQ1 = 19000  # Hz (1-bit)
BIT_RATE = 100        # bits/sec

def text_to_bits(text):
    """Convert text to array of bits"""
    return np.array([int(bit) for char in text for bit in format(ord(char), '08b')])

def generate_packet(message):
    """Add preamble and convert to bits"""
    preamble = [1,0,1,0,1,0]  # Simple alternating preamble
    message_bits = text_to_bits(message)
    return np.concatenate([preamble, message_bits])

def main():
    parser = argparse.ArgumentParser(description='FSK Audio Sender')
    parser.add_argument('--f0', type=float, default=DEFAULT_FREQ0, help='Frequency for 0-bit')
    parser.add_argument('--f1', type=float, default=DEFAULT_FREQ1, help='Frequency for 1-bit')
    args = parser.parse_args()

    print(f"FSK Sender ready (0={args.f0}Hz, 1={args.f1}Hz)")
    
    while True:
        try:
            message = input("Message to send: ")
            bits = generate_packet(message)
            signal = modulate_fsk(bits, SAMPLE_RATE, args.f0, args.f1, BIT_RATE)
            
            # Play audio
            sd.play(signal, SAMPLE_RATE, blocking=True)
            print("Message sent!")
            
        except KeyboardInterrupt:
            print("\nExiting sender...")
            break

if __name__ == "__main__":
    main()