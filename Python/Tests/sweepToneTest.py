import numpy as np
import sounddevice as sd

"""
Sweep Tone Test: for testing the best range of frequencies to use for a receiving microphone 
===============================
By Aaron Hassan Robinson
This code should be used to calibrate a microphone/ receiver being used, along side an oscilloscope 
"""


# Sweep parameters
duration = 10  # seconds for the full sweep
start_freq = 20      # Start frequency in Hz (avoid true 0Hz to prevent speaker stress)
end_freq = 20000     # End frequency in Hz
sample_rate = 44100  # CD quality audio

# Time array
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Logarithmic or linear sweep (choose one)
# Linear sweep
sweep = np.sin(2 * np.pi * (start_freq + (end_freq - start_freq) * t / duration) * t)

# Play the sound
print(f"Playing frequency sweep from {start_freq} Hz to {end_freq} Hz over {duration} seconds...")
sd.play(sweep, samplerate=sample_rate)
sd.wait()
print("Done.")