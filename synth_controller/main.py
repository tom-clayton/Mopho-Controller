
from ui import MainScreen
from setup_manager import SetupManager, NoSetupException
from controller_manager import ControllerManager
from synth_manager import SynthManager
from midi import Midi
from patch_manager import PatchManager
from strings import *

from kivy.app import App
from kivy.core.window import Window

import sys

class MainApp(App):
    """Controls manager objects"""
    def __init__(self, **kwargs):
        """Create manager objects"""
        super(MainApp, self).__init__(**kwargs)

        Window.size = (1200, 800)
        #Window.size = (400, 400)

        # init ui
        self.ui = MainScreen()

        # init setup manager
        try:
            self.setup_manager = SetupManager(self.ui)
        except NoSetupException:
            print("no setup")
            sys.exit(1)

        # init screens
        screens = self.setup_manager.build_screens()

        # init controller manager
        self.controller_manager = ControllerManager(screens)                                      screens

        # init synth manager
        self.synth_manager = SynthManager(self.controller_manager.synths)

        # init midi interface
        self.midi = Midi(self.on_incoming_cc, self.on_incoming_sysex)

        # init patch manager
        self.patch_manager = PatchManager(
                                self.midi,
                                self.ui,
                                self.controller_manager,
                                self.synth_data,
                                self.on_no_patch_details_error
                            ) 

    def build(self):
        """build the kivy app"""
        return self.ui

    def on_start(self):
        """check if synths have a midi channel registered in settings file.
        initialise controllers with synth options lists and
        callbacks to bind to controller events.
        Assign and set midi channels.""" 
        self.controller_manager.initialise_controllers(
            self.synth_manager.options_lists
            self.midi.send_nrpn,
            self.patch_manager.on_load_unconfirmed
        )
        
        self.setup_manager.assign_channels()
        self.controller_manager.set_channels(self.setup_manager.channels)

        #self.ui.simple_popup("Welcome", "Synth Controller")

    # midi callbacks #    
    def on_incoming_cc(self, channel, nrpn, value):
        """Set and display controller value from incoming midi"""
        self.controller_manager.set_controller_value(channel, nrpn, value)
        
    def on_incoming_sysex(self, message):
        """Parse incoming sysex message"""
        patch_manager.parse_sysex(message)


    # functions to be moved to patch_manager class: #
    def _on_save_unconfirmed(self, _, data):
        """open a confirm popup to confirm patch save if file alreadey exists
    else save file"""
        synth, filename = data
        if not patch_manager.check_synth(synth):
            print(NO_PATCH_ABILITY)
        if os.path.exists(filename):
            self.ui.confirm_popup(CONFIRM_SAVE, 'on_save_confirmed', data)
        else:
            patch_manager.save_patch(synth, filename)
        
    def _on_save(self, _, data):
        """get nrpn values in dump order for given synth, save to file"""
        synth, filename = data
        print("save", synth, filename)
        return
        save_data = self.controller_manager.get_controller_values(
                                        synth,
                                        self.synths[synth].nrpn_order
                                    )
        
        with open(filename, "wb") as fo:
            fo.write(bytes(save_data))


def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
    main()    
