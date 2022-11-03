
# To add a patching ability to a registered synth:

# A function to unpack the sysex message must be added to this file and
# referenced in the FUNCTIONS dict.

# The following key-value pairs must be added to the synth's json file:

# "unpack function" : The key from the FUNCTIONS dict below. 

# "recive data" : The initial bytes of a recieve patch message from the
#                 synth so it can be recognised as a patch.
#                 As a string of hex, without leading 0x.

# "program dump request" : The sysex message required to request a program
#                          dump from the synth

# "nrpn order" : The order that the nrpn parameters come in a patch
#                message. As a list of ints.

# See mopho's json file for an example.

def mopho_unpack(data):
    """Unpack midi patch dump data into tuple of parameter values as ints.
    Packing format from page 44 of Manual"""
    unpacked_data = []

    for i in range(0, len(data), 8):
        chunk = data[i: i+8]
        packing_byte = chunk[0]
        mask = 0x01
        for byte in chunk[1:]:
            unpacked_data.append(((packing_byte & mask) << 7) | byte)
            mask <<= 1

    return tuple(unpacked_data)

def mopho_pack(data):
    """Pack midi patch dump data from tuple of parameter values as ints.
    Packing format from page 44 of Manual"""
    packed_data = []

    for i in range(0, len(data), 7):
        chunk = data[i: i+7]
        packing_byte = 0x0
        data_bytes = []
        shift = 0x7
        for byte in chunk:
            packing_byte |= ((byte & 0x80) >> shift)
            shift -= 1
            data_bytes.append(byte & 0x7f)
            
        packed_data.append(packing_byte)
        packed_data.extend(data_bytes)

    return tuple(packed_data)
    

FUNCTIONS = {
    'mopho_unpack': mopho_unpack,
    'mopho_pack': mopho_pack,
}
