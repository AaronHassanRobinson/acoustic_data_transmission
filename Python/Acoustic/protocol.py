### contains protocol definitions and information for data serialisation 
###
### Send chars 
PLAIN_TEXT_HEADER_TYPE = 0
# format for making a plaintext header 
#PLAIN_TEXT_HEADER = struct.pack('!BH', message_type, message_len)  # Big-endian format

#todo: ideally this will apply a header to a msg, 
def encode_packet():
    pass

#todo: ideally this will strip and decode a header + the msg 
def decode_packet():
    pass

# sync marker: 
#[todo]: adjust some sort of timing window based on the preamble note duration
def detect_preamble(bits, PREAMBLE = [1,0,1,0,1,0,1,0]):
    preamble_str = ''.join(map(str, PREAMBLE))
    bits_str = ''.join(map(str, bits))
    index = bits_str.find(preamble_str)
    return index if index != -1 else None


