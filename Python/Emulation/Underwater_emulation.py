import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, butter, lfilter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Acoustic import *
"""
Under water acoustic transmission emulation code
===============================
By Aaron Hassan Robinson
This code emulates conditions underwater for FSK acoustic data transmission
"""

# ==============================
# Parameters
# ==============================
sample_rate_fs = 88200                  # Sampling rate (Hz)
bit_rate = 650             # Bits per second
f0  = 41000           
f1 = 39000        # Frequencies for 0 and 1 (Hz)
guard_band = 100 #  guard band
preamble = np.array([1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0])  # Barker code
samples_per_bit = int(sample_rate_fs / bit_rate)

SPEED_OF_SOUND = 1447  
# speed of sound in water 10 degrees celsius. source: https://www.omnicalculator.com/physics/speed-of-sound
# adjust as needed 
DISTANCE_M = 100
MEDIUM_TYPE = "none"

# Generate random data then append preamble @ the start: 
data_bits = np.random.randint(0, 2, 21)
tx_bits = np.concatenate([preamble, data_bits])

tx_signal = modulate_fsk(bits=tx_bits, sample_rate=sample_rate_fs, freq0=f0, freq1=f1,bit_rate=bit_rate)

 # Absorption loss (Thorp formula for frequencies > 400 Hz)
        # source for this: https://gorbatschow.github.io/SonarDocs/sound_absorption_sea_thorp.en/#octavematlab-implementation 
# Thorp, William H, "Analytic description of the low‐frequency attenuation coefficient", 1967

# todo: could probably make this it's own class 
# Underwater Channel Effects
def add_channel_effects(signal, distance_m, medium='saltwater', temp_c=10, salinity_ppt=35, depth_m=100):
    """
    Simulates underwater acoustic channel effects
    
    Args:
        signal (np.array): Input signal
        distance_m (float): Distance from source in meters
        medium (str): Water type ('saltwater', 'freshwater', 'coastal', 'arctic')
        temp_c (float): Water temperature in °C
        salinity_ppt (float): Salinity in parts per thousand
        depth_m (float): Depth in meters
        
    Returns:
        np.array: Signal with channel effects
    """
    # Normalize signal first
    signal = signal / np.max(np.abs(signal))
    
    # 1. Calculate attenuation
    def get_attenuation(freq, distance):
        """Combines spreading and absorption loss"""
        if medium == 'none':  # for testing without any channel affects
            return 0  # 0 dB total loss
        # Spreading loss (cylindrical)
        # according to formula: TLspread​=10log10​(r) (r = distance (m))
        spreading_loss = 10 * np.log10(distance)  # dB
        
        # example test for different environments: For best accuracy,
        # the user should fill in stats depending on the water they are in
        # Absorption loss (Thorp formula for frequencies > 400 Hz)
        # Thorp's equation (dB/km)
        # source for this: https://gorbatschow.github.io/SonarDocs/sound_absorption_sea_thorp.en/#octavematlab-implementation 
        if medium == 'saltwater':
            f_kHz = freq / 1000  
    
            # Apply the Thorp formula from the source
            alpha = 1.0936 * (
                0.1 * (f_kHz**2) / (1 + f_kHz**2) + 
                40 * (f_kHz**2) / (4100 + f_kHz**2)
            )
            absorption  = alpha * (distance_m / 1000) 
            # ideally would measure these values where you were deploying for best accuracy. 
        elif medium == 'freshwater':
            #todo: 
            pass
        elif medium == 'coastal':
             #todo: 
            pass
        elif medium == 'arctic':
             #todo: 
            pass
        else:
            raise ValueError(f"Unknown medium: {medium}")
        
        absorption_loss = absorption * (distance/1000)  # Convert to dB, div to convrt to km
        
        return spreading_loss + absorption_loss
    
    # 2. Apply frequency-dependent attenuation 
    center_freq = (f0 + f1)/2
    total_loss_db = get_attenuation(center_freq, distance_m)
    attenuation = 10**(-total_loss_db/20)  # Convert dB to linear
    
    # 3. Apply basic multipath time spreading
    # using formula: delay_spread=distanc/sound_speede​×sample_rate
    delay_spread = int((distance_m / SPEED_OF_SOUND) * sample_rate_fs) 
    multipath = 0.4 * np.roll(signal, delay_spread)
    multipath[:delay_spread] = 0
    
    
    # example test for different environments: the user should fill in stats depending on the water they are in
    # 4. Add environmental noise
    def ambient_noise(freq):
        """Wenz curve approximation for ambient noise"""
        if medium == 'arctic':
            return 1e-4  # Quieter environment
        return 5e-4 * (freq/1000)**-1.5  # Frequency-dependent noise
    
    noise_level = ambient_noise(center_freq) * np.random.randn(len(signal))
    
    # 5. Combine all effects
    attenuated_signal = signal * attenuation
    noisy_signal = attenuated_signal + multipath + noise_level
    
    return noisy_signal / np.max(np.abs(noisy_signal))  # Renormalize


#rx_signal = add_channel_effects(signal=tx_signal, distance_m=DISTANCE_M, medium=MEDIUM_TYPE)

rx_signal = tx_signal
# Apply bandpass filter
lowcut = min(f0, f1) - guard_band 
highcut = max(f0, f1) + guard_band
filtered_signal = bandpass_filter(rx_signal, lowcut, highcut, sample_rate_fs)


# [todo]: investigate if this is the best way to detect preamble
def detect_preamble(signal, preamble):
    # generates a signal, then compares the  signal read with the known generated one 
    # todo: swap this out with the one that compares the bits 
    preamble_signal = modulate_fsk(bits=preamble, sample_rate=sample_rate_fs, freq0=f0, freq1=f1,bit_rate=bit_rate)
    correlation = correlate(signal, preamble_signal, mode='full')
    peak_idx = np.argmax(correlation)
    return peak_idx - len(preamble_signal) + 1  # Proper correlation offset


# Detect preamble and demodulate (using filtered signal)
preamble_start = detect_preamble(filtered_signal, preamble)
#rx_bits = demodulate_fsk(filtered_signal, preamble_start + len(preamble) * samples_per_bit)
rx_bits = demodulate_fsk(signal=filtered_signal, sample_rate=sample_rate_fs, freq0=f0, freq1=f1, bit_rate=bit_rate, start_index=preamble_start + len(preamble)* samples_per_bit )


# Bit Error Rate (BER)
min_len = min(len(rx_bits), len(data_bits))
ber = np.sum(np.abs(rx_bits[:min_len] - data_bits[:min_len])) / min_len
print(f"Bit Error Rate (BER): {ber:.4f}")

# ==============================
#  Plotting
# ==============================
def plot_tx_rx_filtered(expected_bits, rx_bits, tx_signal, rx_signal, filtered_signal, samples_per_bit, distance=0, medium="unknown", temp=10): 
    
    # Plot 1: Transmitted signal with bits
    plt.subplot(4, 1, 1)
    plt.plot(tx_signal[:20*samples_per_bit], 'b-', label="Transmitted FSK", linewidth=0.25)
    for i, bit in enumerate(tx_bits[:20]):
        bit_x = i * samples_per_bit + samples_per_bit//2
        plt.text(bit_x, 0.9, str(bit), ha='center', color='red', fontweight='bold')
    plt.title(f"Bit rate: {bit_rate}BPS\nTransmitted Signal with Embedded Bits @ frequencies: digital 1 ={f1}Hz, digital 0 ={f0}Hz")
    plt.xlabel("Time (samples)")
    plt.ylabel("Amplitude") 
    plt.grid(True)
    plt.legend()

    # Plot 2: Raw received signal (noisy)
    plt.subplot(4, 1, 2)
    plt.plot(rx_signal[:20*samples_per_bit], 'g-', alpha=0.7, label="Received (Noisy)")
    plt.title(
        #f"Ambient noise added:"
        f"Raw Received Signal\n"
        #f"Distance: {distance}m | Medium: {medium.title()}\n"
        #f"Temp: {temp}°C | Pre-Filter BER: {ber:.4f}"
    )
    plt.xlabel("Time (samples)")
    plt.ylabel("Amplitude") 
    plt.grid(True)
    plt.legend()

    # Plot 3: Filtered signal
    plt.subplot(4, 1, 3)
    plt.plot(filtered_signal[:20*samples_per_bit], 'm-', label="Filtered Signal")
    plt.title(f"Bandpass Filtered ({lowcut/1000:.1f}kHz-{highcut/1000:.1f}kHz)")
    plt.xlabel("Time (samples)")
    plt.ylabel("Amplitude") 
    plt.grid(True)
    plt.legend()

    # Plot 4: Bit comparison
    plt.subplot(4, 1, 4)
    plt.step(range(20), expected_bits[:20], 'b-', where='mid', label="Transmitted")
    plt.step(range(20), rx_bits[:20], 'r--', where='mid', label="Received")
    plt.title("Bit Comparison (Errors Marked)")
    # For plot 4:
    plt.xlabel("Bit Position")
    plt.ylabel("Binary Value")
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
    samples_per_bit=samples_per_bit,
    distance=DISTANCE_M,
    medium=MEDIUM_TYPE
)