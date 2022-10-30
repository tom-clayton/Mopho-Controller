
import os
import json
import synth_functions as functions

SYNTHS_DIR = 'synths'

FUNCTIONs = {
    'mopho': {
        'check': mopho_check_patch,
        'unpack': mopho_unpack
    }
}

class SynthManager(object):
    """Manages data and unique functions of synths"""
    def __init__(self):
        """get list of available synths"""
        self.synths_dir = os.path.join(os.getcwd(), SYNTHS_DIR)
        self.settings_files = [f[:-5] for f in os.listdir(self.synths_dir)\
                               if f[-5:] == '.json']
        self.python_files = [f[:-3] for f in os.listdir(self.synths_dir)\
                               if f[-3:] == '.py']

    def load_synths(self, synths):
        """load data for each synth in 'synths', put in a dict with None
        as value if no data found.
        Return dict of options lists for each synth."""
        self.synths = {}
        for synth in synths:
            if synth in self.settings_files:
                self.synths[synth] = SynthData(
                            os.path.join(self.synths_dir, synth + '.json')
                        ) 
            else:
                self.synths[synth] = None

        self.load_functions()            

    @property
    def options_lists(self)
        output = {}
        for synth in self.synths:
            try:
                output[synth] = self.synths[synth].options_lists
            except NoOptionsError:
                pass
        return output
        
class SynthData(object):
    """Object representing each synth"""
    def __init__(self, filename):
        """load the json data"""
        with open(filename) as fo:
            self.data = json.load(fo)

    @property
    def options_lists(self):
        try:
            return self.data['options']
        except KeyError:
            raise NoOptionsError

class NoOptionsError(Exception):
    pass
