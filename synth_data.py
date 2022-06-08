
import os
import json

SYNTHS_DIR = 'synths'

class SynthDataLoader(object):
    def __init__(self):
        """get list of available synths"""
        self.synths_dir = os.path.join(os.getcwd(), SYNTHS_DIR)
        self.available = [f[:-5] for f in os.listdir(self.synths_dir)\
                           if f[-5:] == '.json']

    def load(self, synths):
        """load data for each synth in 'synths', put in a dict with None
        as value if no data found"""
        output = {}
        for synth in synths:
            if synth in self.available:
                output[synth] = SynthData(
                                    os.path.join(self.synths_dir, synth + '.json')
                                )
            else:
                output[synth] = None

        return output
        
class SynthData(object):
    def __init__(self, synth):
        """load the json data"""
        with open(synth) as fo:
            self.data = json.load(fo)
        
