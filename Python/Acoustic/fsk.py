# python/acoustic/fsk.py
# [todo]: might switch to scipy library for simplicity and consistency
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

#[todo]: switch to scipy library instead of implementing these myself
# code partially from DeepSeek lmao 
def demodulate_fsk(signal, sample_rate=44100, freq0=1000, freq1=2000, bit_rate=10, start_index=0):
    """
    Demodulates FSK audio signal to bits using FFT with improved robustness
    
    Args:
        signal (np.array): Audio signal to demodulate
        sample_rate (int): Sampling rate in Hz
        freq0 (float): Frequency for 0 bits
        freq1 (float): Frequency for 1 bits
        bit_rate (float): Data rate in bits per second
        start_index (int): Sample index to start decoding from (skip preamble)
        
    Returns:
        list: Demodulated bits
    """
    samples_per_bit = int(sample_rate / bit_rate)
    bits = []
    
    # Add windowing and neighborhood check parameters
    neighborhood = 2  # bins to check around target frequency
    window = np.hanning(samples_per_bit)  # Pre-calculate window
    
    for i in range(start_index, len(signal), samples_per_bit):
        #window = np.hanning(len(chunk)) 
        chunk = signal[i:i+samples_per_bit]
        if len(chunk) < samples_per_bit:
            break  # Skip partial bits at end

        # Apply window function to reduce spectral leakage
        windowed_chunk = chunk * window
        
        # Compute FFT and magnitudes
        fft = np.fft.fft(windowed_chunk)
        magnitudes = np.abs(fft)
        
        # Calculate frequency bins with neighborhood check
        n = len(chunk)
        max_bin = n // 2
        
        def get_max_energy(target_freq):
            bin_center = int(target_freq * n / sample_rate)
            bin_start = max(0, bin_center - neighborhood)
            bin_end = min(max_bin, bin_center + neighborhood + 1)
            return np.max(magnitudes[bin_start:bin_end])
        
        energy0 = get_max_energy(freq0)
        energy1 = get_max_energy(freq1)
        
        bits.append(1 if energy1 > energy0 else 0)
    
    return bits


