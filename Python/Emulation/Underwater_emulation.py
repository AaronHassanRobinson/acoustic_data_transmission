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
bit_rate = 550              # Bits per second
f0  = 500           
f1 = 1500        # Frequencies for 0 and 1 (Hz)
guard_band = 100 # 100hz guard band
preamble = np.array([1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0])  # Barker code
samples_per_bit = int(sample_rate_fs / bit_rate)



# Generate random data + preamble
data_bits = np.random.randint(0, 2, 21)
tx_bits = np.concatenate([preamble, data_bits])

tx_signal = modulate_fsk(bits=tx_bits, sample_rate=sample_rate_fs, freq0=f0, freq1=f1,bit_rate=bit_rate)

# ==============================
# Underwater Channel Effects
# ==============================
def add_channel_effects(signal):
    signal = signal / np.max(np.abs(signal))  ## Normalise signal 
    # Add noise (AWGN)
    noise = 0.2 * np.random.randn(len(signal))
    noisy_signal = signal + noise
    
    # Add multipath (delayed echo)
    delay = int(0.5 * samples_per_bit)
    multipath = 0.3 * np.roll(signal, delay)
    multipath[:delay] = 0
    
    return noisy_signal + multipath

rx_signal = add_channel_effects(tx_signal)



# Apply bandpass filter
lowcut = min(f0, f1) - guard_band  # 500Hz guard band
highcut = max(f0, f1) + guard_band
filtered_signal = bandpass_filter(rx_signal, lowcut, highcut, sample_rate_fs)

# ==============================
# Receiver
# ==============================
# [todo]: investigate if this is the best way to detect preamble
def detect_preamble(signal, preamble):
    preamble_signal = modulate_fsk(bits=preamble, sample_rate=sample_rate_fs, freq0=f0, freq1=f1,bit_rate=bit_rate)
    correlation = correlate(signal, preamble_signal, mode='full')
    peak_idx = np.argmax(correlation)
    return peak_idx - len(preamble_signal) + 1  # Proper correlation offset


# Detect preamble and demodulate (using filtered signal)
preamble_start = detect_preamble(filtered_signal, preamble)
#rx_bits = demodulate_fsk(filtered_signal, preamble_start + len(preamble) * samples_per_bit)
rx_bits = demodulate_fsk(signal=filtered_signal, sample_rate=sample_rate_fs, freq0=f0, freq1=f1, bit_rate=bit_rate, start_index=preamble_start + len(preamble)* samples_per_bit )
# ==============================
# Analysis
# ==============================
# Bit Error Rate (BER)
min_len = min(len(rx_bits), len(data_bits))
ber = np.sum(np.abs(rx_bits[:min_len] - data_bits[:min_len])) / min_len
print(f"Bit Error Rate (BER): {ber:.4f}")

# ==============================
# Enhanced Plotting with Filtering
# ==============================
def plot_tx_rx_filtered(expected_bits, rx_bits, tx_signal, rx_signal, filtered_signal, samples_per_bit): 
    
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
    plt.step(range(20), expected_bits[:20], 'b-', where='mid', label="Transmitted")
    plt.step(range(20), rx_bits[:20], 'r--', where='mid', label="Received")
    plt.title("Bit Comparison (Errors Marked)")
    plt.yticks([0, 1])
    plt.grid(True)
    
    # Mark bit errors
    error_count = 0
    for i, (expected_bits, rx_bit) in enumerate(zip(expected_bits[:20], rx_bits[:20])):
        if expected_bits != rx_bit:
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
plot_tx_rx_filtered(
    expected_bits=data_bits,  
    rx_bits=rx_bits,
    tx_signal=tx_signal,
    rx_signal=rx_signal,
    filtered_signal=filtered_signal,
    samples_per_bit=samples_per_bit
)