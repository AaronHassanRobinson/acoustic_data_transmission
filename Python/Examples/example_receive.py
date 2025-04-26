# example_receive.py

import argparse
import sounddevice as sd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Acoustic import demodulate_fsk

# Configuration
SAMPLE_RATE = 44100
BUFFER_SECONDS = 1
DEFAULT_FREQ0 = 18000
DEFAULT_FREQ1 = 19000
BIT_RATE = 100

def bits_to_text(bits):
    """Convert array of bits to text"""
    chars = []
    for i in range(0, len(bits)//8):
        byte = bits[i*8:(i+1)*8]
        chars.append(chr(int(''.join(map(str, byte)), 2)))
    return ''.join(chars)

class Receiver:
    def __init__(self, freq0, freq1):
        self.freq0 = freq0
        self.freq1 = freq1
        self.buffer = np.array([])
        self.in_message = False
        self.bits = []
        
    def audio_callback(self, indata, frames, time, status):
        """Called for each audio chunk"""
        self.buffer = np.concatenate([self.buffer, indata[:,0]])
        
        # Detect preamble
        if not self.in_message:
            if len(self.buffer) > SAMPLE_RATE:  # Look in last second of audio
                # Simple energy detection
                if np.max(self.buffer[-SAMPLE_RATE:]) > 0.1:
                    self.in_message = True
                    self.buffer = np.array([])
                    print("\nMessage detected...")
        
        # Demodulate when in message mode
        if self.in_message:
            bits = demodulate_fsk(self.buffer, SAMPLE_RATE, self.freq0, self.freq1, BIT_RATE)
            if bits:
                self.bits.extend(bits)
                self.buffer = self.buffer[len(bits)*int(SAMPLE_RATE/BIT_RATE):]
                
                # Try decoding
                try:
                    text = bits_to_text(self.bits)
                    if len(text) > 0:
                        print(f"\nReceived: {text}", end='\n> ', flush=True)
                        self.reset()
                except:
                    self.reset()

    def reset(self):
        self.in_message = False
        self.bits = []
        self.buffer = np.array([])

def main():
    parser = argparse.ArgumentParser(description='FSK Audio Receiver')
    parser.add_argument('--f0', type=float, default=DEFAULT_FREQ0, help='Frequency for 0-bit')
    parser.add_argument('--f1', type=float, default=DEFAULT_FREQ1, help='Frequency for 1-bit')
    args = parser.parse_args()

    receiver = Receiver(args.f0, args.f1)
    
    print(f"FSK Receiver listening (0={args.f0}Hz, 1={args.f1}Hz)...")
    
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=receiver.audio_callback):
        while True:
            try:
                input("Press Enter to exit...")
                break
            except KeyboardInterrupt:
                print("\nExiting receiver...")
                break

if __name__ == "__main__":
    main()