### contains protocol definitions and information for data serialisation 
###
### Send chars 
PLAIN_TEXT_HEADER_TYPE = 0
# format for making a plaintext header 
#PLAIN_TEXT_HEADER = struct.pack('!BH', message_type, message_len)  # Big-endian format


def encode_packet():
    pass

def decode_packet():
    pass

def detect_preamble(bits, PREAMBLE = [1,0,1,0,1,0,1,0]):
    preamble_str = ''.join(map(str, PREAMBLE))
    bits_str = ''.join(map(str, bits))
    index = bits_str.find(preamble_str)
    return index if index != -1 else None


