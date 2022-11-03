
import os
import json
import synths.packing_functions as functions

SYNTHS_DIR = 'synths'

class SynthManager(object):
    """Manages data and unique functions of synths"""
    def __init__(self, synths):
        """get list of available synths"""
        self.synths_dir = os.path.join(os.getcwd(), SYNTHS_DIR)
        self.settings_files = [f[:-5] for f in os.listdir(self.synths_dir)\
                               if f[-5:] == '.json']
        self._load_synths(synths)

    def _load_synths(self, synths):
        """load data for each synth in 'synths' directory, put in a dict
        with None as value if no data found."""
        self.synths = {}
        for synth in synths:
            if synth in self.settings_files:
                self.synths[synth] = SynthData(
                            os.path.join(self.synths_dir, synth + '.json'),
                            synth
                        ) 
            else:
                self.synths[synth] = None

    def is_patchable(self, synth):
        """Return true if given synth has the required details to allow
        patching"""
        return self.synths[synth].patchable

    def find_synth(self, message):
        """Return the synth that the message is for."""
        for synth in self.synths:
            header = self.synths[synth].header
            if header == message[:len(header)]:
                return synth
        return None

    def unpack(self, synth, data):
        """Unpack the received data according to the given synth's unpack function"""
        return self.synths[synth].check_and_unpack(data)

    def pack(self, synth, data):
        """Pack the data according to the given synth's pack function"""
        return self.synths[synth].pack(data)

    def get_order(self, synth):
        """Return the given synth's nrpn order"""
        return self.synths[synth].nrpn_order

    def get_header(self, synth):
        """Return the patch header for given synth"""
        return self.synths[synth].header

    def get_request(self, synth):
        """Return the patch request header for given synth"""
        return self.synths[synth].patch_request   

    @property
    def options_lists(self):
        output = {}
        for synth in self.synths:
            output[synth] = self.synths[synth].options
        return output
        
class SynthData(object):
    """Object representing each synth"""
    def __init__(self, filename, synth):
        """load the json data"""
        self.synth = synth
        with open(filename) as fo:
            data = json.load(fo)

        try:
            self.options = data['options']
        except KeyError:
            self.options = None
        
        if all(map(lambda x: x in data, [
                            'unpack function',
                            'pack function',
                            'receive header',
                            'parameters'
                            'patch request'
                        ])):
            self.patchable = True
            self._load_patching_details(data)
        else:
            self.patchable = False        

    def _load_patching_details(self, data):
        """load patching details from settings file"""
        self.header = bytes.fromhex(data['receive header'])
        self.unpack = functions.FUNCTIONS[data['unpack function']]
        self.pack = functions.FUNCTIONS[data['pack function']]
        self.patch_request = bytes.fromhex(data['patch request'])
        self.n_parameters = data['parameters']

        if 'nrpn order' not in data:
            self.nrpn_order = list(range(0, self.n_parameters)
        elif self.n_parameters > len(data['nrpn order']):
            self.nrpn_order = data['nrpn order']\
                + list(range(len(data['nrpn order']), self.n_parameters)
        elif self.n_parameters < len(data['nrpn order']):
            self.nrpn_order = data['nrpn order'][:self.n_parameters]
        else:
            self.nrpn_order = data['nrpn order']

    def check_and_unpack(self, message):
        """Check receive data message is for this synth then unpack using
        unpack function"""
        if self.header == message[:len(self.header)]:
            return self.unpack(message[len(self.header):])
        else:
            raise IncorrectSynthError

    def pack(self, data):
        """Pack the data and add its header"""
        return self.header + self.pack(data)
        
class IncorrectSynthError(Exception):
    pass
