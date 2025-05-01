# acoustic_data_transmission

### Acoustic - Python module for Acoustic FSK

to use: include this at the top of your file (if in a folder in the Python dir)

```
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

#### codec.py - packing and unpacking fuctions

pack_bits: a simple function that will convert some given text into an array of bits

unpack bits: a function that takes in a group of bits, and converts it back into plain text 

^^ todo: make these specific to text, want to eventually add other data formats

#### constants.py - a shared constants document

The user can override values in this file, and import this to use as a shared document between sending and receiving architectures


#### FSK.py - modulation and demodulation techniques for Frequency shift keying

modulate_fsk and demodulate_fsk are two functions that can be used in tandem in a sender, receiver fashion. These two functions are set to default values, however these can be changed by the user to suit their purposes


#### FSK.py - modulation and demodulation techniques for Frequency shift keying

