# python/acoustic/fsk.py

import numpy as np


# bit : Samples per 
def modulate_fsk(bits, sample_rate=44100, freq0=1000, freq1=2000, bit_rate=0.1):
    """
    Modulates bits into FSK audio signal
    
    Args:
        bits (array): Array of 0s and 1s to modulate
        sample_rate (int): Sampling rate in Hz
        freq0 (float): Frequency for 0 bits
        freq1 (float): Frequency for 1 bits
        bit_rate (float): bits per second to send
        
    Returns:
        np.array: Generated audio signal
    """
    samples_per_bit = int(sample_rate / bit_rate)
    t = np.linspace(0, 1/bit_rate, samples_per_bit, endpoint=False)
    
    signal = np.array([])
    
    for bit in bits:
        frequency = freq1 if bit else freq0
        samples = np.sin(2 * np.pi * frequency * t)
        signal = np.concatenate((signal, samples))
    
    return signal


def demodulate_fsk():
    pass



