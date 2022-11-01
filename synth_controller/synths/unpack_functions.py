
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

FUNCTIONS = {
    'mopho_unpack': mopho_unpack,
    }

def mopho_unpack(data):
    """Unpack midi patch dump data into tuple of parameter values
    as ints. Packing format from page 44 of Manual"""
    unpacked_data = []

    for i in range(0, len(data), 8):
        chunk = data[i: i+8]
        packing_byte = chunk[0]
        mask = 0x01
        for byte in chunk[1:]:
            if (packing_byte & mask):
                unpacked_data.append(0x80 + byte)
            else:
                unpacked_data.append(byte)
            mask = mask << 1

    return tuple(unpacked_data)
