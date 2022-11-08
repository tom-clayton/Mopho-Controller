
# Loads and displays patch data from sysex file

#import sys
#print(sys.path)

import os
os.chdir("E:\\Synth-Controller\\synth_controller")

from synth_manager import SynthManager
from patch_manager import PatchManager

FILENAME = "m_test2.sysex"
SYNTH = 'mopho'

class DummyUI(object):
    def bind(self, on_load_confirmed):
        pass

class DummyControllerManager(object):
    def set_controller_values(self, synth, order, data):
        for i, nrpn in enumerate(order):
            print(f"{nrpn} : {data[i]}")


synth_manager = SynthManager([SYNTH])
            
patch_manager = PatchManager(
    None,
    DummyUI(),
    DummyControllerManager(),
    synth_manager,
    None
)

os.chdir("E:\\Synth-Controller\\tests")
patch_manager.on_load_confirmed([SYNTH, FILENAME])    
    
