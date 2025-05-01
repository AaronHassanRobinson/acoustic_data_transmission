def pack_bits(text):
    #todo: document
    bits = []
    for char in text:
        bits.extend(int(b) for b in format(ord(char), '08b'))
    return bits
    
def unpack_bits(bitgroups):
    chars = []
    for bits in bitgroups:
        byte = bits
        if len(byte) == 8:
            chars.append(chr(int(''.join(map(str, byte)), 2)))
    return ''.join(chars)