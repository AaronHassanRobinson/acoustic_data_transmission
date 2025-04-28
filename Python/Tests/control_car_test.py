import tkinter as tk
import sounddevice as sd
import numpy as np
import threading
import time

# Sampling parameters
SAMPLE_RATE = 44100
DURATION = 0.25  # Duration of each tone in seconds

# FSK Binary protocol frequencies (Hz)
FREQ_START = 200
FREQ_STOP = 1000
FREQ_0 = 340
FREQ_1 = 410

# Movement control tones
FREQ_FORWARD = 480
FREQ_LEFT = 550
FREQ_RIGHT = 620
FREQ_BACKWARDS = 690
FREQ_STRAIGHTEN = 530  # New frequency for "straighten"

# Function to generate and play a tone
def play_tone(freq, duration=DURATION):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * freq * t)
    sd.play(tone, SAMPLE_RATE)
    sd.wait()

# Send a character as 8-bit binary via FSK
def send_char(c):
    byte = format(ord(c), '08b')
    threading.Thread(target=transmit_binary, args=(byte,)).start()

def transmit_binary(bits):
    print(f"Sending character as bits: {bits}")
    play_tone(FREQ_START)
    time.sleep(0.05)

    for bit in bits:
        if bit == '0':
            play_tone(FREQ_0)
        elif bit == '1':
            play_tone(FREQ_1)
        time.sleep(0.05)

    play_tone(FREQ_STOP)

# Movement control transmission
def send_movement_command(direction):
    freq_map = {
        'W': FREQ_FORWARD,
        'A': FREQ_LEFT,
        'D': FREQ_RIGHT,
        'S': FREQ_BACKWARDS,
        'SPACE': FREQ_STRAIGHTEN
    }
    freq = freq_map.get(direction.upper())
    if freq:
        threading.Thread(target=transmit_movement, args=(freq,)).start()

def transmit_movement(freq):
    print(f"Sending movement command tone: {freq} Hz")
    play_tone(freq)

# GUI
def create_gui():
    root = tk.Tk()
    root.title("FSK Tone Sender")
    root.geometry("400x400")

    entry_label = tk.Label(root, text="Enter text to send via FSK:")
    entry_label.pack(pady=5)

    entry = tk.Entry(root, font=("Arial", 14))
    entry.pack(pady=5)

    def send_text():
        text = entry.get()
        for c in text:
            send_char(c)
            time.sleep(0.3)

    send_button = tk.Button(root, text="Send Text", command=send_text, font=("Arial", 12))
    send_button.pack(pady=10)

    control_label = tk.Label(root, text="Control the Vehicle (W/A/S/D/SPACE):")
    control_label.pack(pady=10)

    control_frame = tk.Frame(root)
    control_frame.pack()

    # Movement buttons
    btn_w = tk.Button(control_frame, text="↑ W", width=10, height=2, command=lambda: send_movement_command('W'))
    btn_a = tk.Button(control_frame, text="← A", width=10, height=2, command=lambda: send_movement_command('A'))
    btn_d = tk.Button(control_frame, text="→ D", width=10, height=2, command=lambda: send_movement_command('D'))
    btn_s = tk.Button(control_frame, text="↓ S", width=10, height=2, command=lambda: send_movement_command('S'))
    btn_space = tk.Button(control_frame, text="⎵ SPACE", width=10, height=2, command=lambda: send_movement_command('SPACE'))

    btn_w.grid(row=0, column=1, padx=5, pady=5)
    btn_a.grid(row=1, column=0, padx=5, pady=5)
    btn_d.grid(row=1, column=2, padx=5, pady=5)
    btn_s.grid(row=2, column=1, padx=5, pady=5)
    btn_space.grid(row=3, column=1, padx=5, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()