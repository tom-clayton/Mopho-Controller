
import os
import json
import unpack_functions as functions

SYNTHS_DIR = 'synths'

class SynthManager(object):
    """Manages data and unique functions of synths"""
    def __init__(self, synths):
        """get list of available synths"""
        self.synths_dir = os.path.join(os.getcwd(), SYNTHS_DIR)
        self.settings_files = [f[:-5] for f in os.listdir(self.synths_dir)\
                               if f[-5:] == '.json']
        self.python_files = [f[:-3] for f in os.listdir(self.synths_dir)\
                               if f[-3:] == '.py']
        self._load_synths(synths)

    def _load_synths(self, synths):
        """load data for each synth in 'synths' directory, put in a dict with None
        as value if no data found.
        Return dict of options lists for each synth."""
        self.synths = {}
        for synth in synths:
            if synth in self.settings_files:
                self.synths[synth] = SynthData(
                            os.path.join(self.synths_dir, synth + '.json', synth)
                        ) 
            else:
                self.synths[synth] = None

    def is_patchable(self, synth):
        """Return true if given synth has the required details to allow
        patching"""
        return self.synths[synth].patchable

    def unpack(self, synth, data):
        """Unpack the receive data according to the given synth's unpack function"""
        return self.synths[synth].check_and_unpack(data)

    def get_order(self, synth):
        """Return the given synth's nrpn order"""
        return self.synths[synth].nrpn_order

    @property
    def options_lists(self)
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
                            'receive data',
                            'nrpn order',
                            'program dump request'
                        ])):
            self.patchable = True
            self._load_patching_details(data)
        else:
            self.patchable = False        

    def _load_patching_details(self, data):
        """load patching details from settings file"""
        self.recieve_header = int(.data['receive data'], 16)\
                            .to_bytes(len(data['receive header'], 'big')
        self.unpack = functions.FUNCTIONS[data['unpack function']]
        self.patch_request = data['patch request']
        self.nrpn_order = data['nrpn order']

    def check_and_unpack(self, message):
        """Check receive data message is for this synth then unpack using
        unpack function"""
        if self.receive_header == message[:len(self.receive_header)]:
            return self.unpack(data[len(self.receive_header):])
        else:
            raise IncorrectSynthError
        
        
class IncorrectSynthError(Exception):
    pass
