import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, butter, lfilter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Acoustic import *
# ==============================
# Parameters
# ==============================
sample_rate_fs = 44100                  # Sampling rate (Hz)
bit_rate = 100              # Bits per second
f0  = 500           
f1 = 1500        # Frequencies for 0 and 1 (Hz)
guard_band = 100 # 100hz guard band
preamble = np.array([1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0])  # Barker code
samples_per_bit = int(sample_rate_fs / bit_rate)

# ==============================
# Transmitter
# ==============================
# def generate_fsk_signal(bits):
#     t = np.linspace(0, 1/bit_rate, samples_per_bit, endpoint=False)
#     signal = np.array([])
#     for bit in bits:
#         freq = f0 if bit == 0 else f1
#         signal = np.append(signal, np.sin(2 * np.pi * freq * t))
#     return signal


# Generate random data + preamble
data_bits = np.random.randint(0, 2, 21)
tx_bits = np.concatenate([preamble, data_bits])

tx_signal = modulate_fsk(bits=tx_bits, sample_rate=sample_rate_fs, freq0=f0, freq1=f1,bit_rate=bit_rate)

# ==============================
# Underwater Channel Effects
# ==============================
def add_channel_effects(signal):
    # Add noise (AWGN)
    noise = 0.2 * np.random.randn(len(signal))
    noisy_signal = signal + noise
    
    # Add multipath (delayed echo)
    delay = int(0.5 * samples_per_bit)
    multipath = 0.3 * np.roll(signal, delay)
    multipath[:delay] = 0
    
    return noisy_signal + multipath

rx_signal = add_channel_effects(tx_signal)

# ==============================
# Filtering
# ==============================
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Apply bandpass filter
lowcut = min(f0, f1) - guard_band  # 500Hz guard band
highcut = max(f0, f1) + guard_band
filtered_signal = bandpass_filter(rx_signal, lowcut, highcut, sample_rate_fs)

# ==============================
# Receiver
# ==============================
def detect_preamble(signal, preamble):
    # Correlate with ideal preamble
    preamble_signal = modulate_fsk(bits=preamble, sample_rate=sample_rate_fs, freq0=f0, freq1=f1,bit_rate=bit_rate)
    correlation = correlate(signal, preamble_signal, mode='valid')
    peak_idx = np.argmax(correlation)
    return peak_idx

def demodulate_fsk(signal, start_idx):
    bits = []
    for i in range(start_idx, len(signal), samples_per_bit):
        chunk = signal[i:i+samples_per_bit]
        if len(chunk) < samples_per_bit:
            break  # Skip incomplete bits
        
        # Create time array for this chunk
        t = np.linspace(0, len(chunk)/sample_rate_fs, len(chunk), endpoint=False)
        
        # Mix with reference frequencies
        mixed_f0 = chunk * np.sin(2 * np.pi * f0 * t)
        mixed_f1 = chunk * np.sin(2 * np.pi * f1 * t)
        
        # Calculate power for each frequency
        power0 = np.sum(np.abs(mixed_f0))
        power1 = np.sum(np.abs(mixed_f1))
        
        bits.append(0 if power0 > power1 else 1)
    #print("received bits:"+ bits)
    return bits

# Detect preamble and demodulate (using filtered signal)
preamble_start = detect_preamble(filtered_signal, preamble)
rx_bits = demodulate_fsk(filtered_signal, preamble_start + len(preamble) * samples_per_bit)

# ==============================
# Analysis
# ==============================
# Bit Error Rate (BER)
ber = np.sum(np.abs(rx_bits - data_bits[:len(rx_bits)])) / len(rx_bits)
print(f"Bit Error Rate (BER): {ber:.4f}")

# ==============================
# Enhanced Plotting with Filtering
# ==============================
def plot_tx_rx_filtered(tx_bits, rx_bits, tx_signal, rx_signal, filtered_signal, samples_per_bit):
    plt.figure(figsize=(12, 10))
    
    # Plot 1: Transmitted signal with bits
    plt.subplot(4, 1, 1)
    plt.plot(tx_signal[:20*samples_per_bit], 'b-', label="Transmitted FSK", linewidth=0.25)
    for i, bit in enumerate(tx_bits[:20]):
        bit_x = i * samples_per_bit + samples_per_bit//2
        plt.text(bit_x, 0.9, str(bit), ha='center', color='red', fontweight='bold')
    plt.title(f"Transmitted Signal with Embedded Bits @ frequencies: digital 1 ={f1}Hz, digital 0 ={f0}Hz")
    plt.grid(True)
    plt.legend()

    # Plot 2: Raw received signal (noisy)
    plt.subplot(4, 1, 2)
    plt.plot(rx_signal[:20*samples_per_bit], 'g-', alpha=0.7, label="Received (Noisy)")
    plt.title(f"Raw Received Signal (Noise + Multipath)\nPre-Filter BER: {ber:.4f}")
    plt.grid(True)
    plt.legend()

    # Plot 3: Filtered signal
    plt.subplot(4, 1, 3)
    plt.plot(filtered_signal[:20*samples_per_bit], 'm-', label="Filtered Signal")
    plt.title(f"Bandpass Filtered ({lowcut/1000:.1f}kHz-{highcut/1000:.1f}kHz)")
    plt.grid(True)
    plt.legend()

    # Plot 4: Bit comparison
    plt.subplot(4, 1, 4)
    plt.step(range(20), tx_bits[:20], 'b-', where='mid', label="Transmitted")
    plt.step(range(20), rx_bits[:20], 'r--', where='mid', label="Received")
    plt.title("Bit Comparison (Errors Marked)")
    plt.yticks([0, 1])
    plt.grid(True)
    
    # Mark bit errors
    error_count = 0
    for i, (tx_bit, rx_bit) in enumerate(zip(tx_bits[:20], rx_bits[:20])):
        if tx_bit != rx_bit:
            plt.scatter(i, 0.5, color='black', marker='x', s=100)
            error_count += 1
    print(f"Total errors: {error_count}")
    print(f"Error percentage: {error_count}")

            
    plt.legend()

    plt.tight_layout()
    plt.show()

# Generate plots
print("data bits:    ", ''.join(str(b) for b in data_bits[:len(rx_bits)]))
print("received bits:", ''.join(str(b) for b in rx_bits))
plot_tx_rx_filtered(tx_bits, rx_bits, tx_signal, rx_signal, filtered_signal, samples_per_bit)