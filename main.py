
from setup_manager import SetupManager, NoSetupException
from midi import Midi
from patch_manager import PatchManager
from controller_manager import ControllerManager
from ui import MainScreen
from synth_manager import SynthManager
from strings import *

from kivy.app import App
from kivy.core.window import Window

import json
import os
import sys
import time


class MainApp(App):
    """Controls manager objects"""
    def __init__(self, **kwargs):
        """Create manager objects"""
        super(MainApp, self).__init__(**kwargs)

        Window.size = (1200, 800)
        #Window.size = (400, 400)

        # init setup manager
        try:
            self.setup_manager = SetupManager()
        except NoSetupException:
            print("no setup")
            sys.exit(1)
            # eventually run as patch librarian if no setup is found.

        # init ui
        self.ui = MainScreen()
        screens = self.ui.build_screens(self.setup_manager.screens)
        self.ui.set_screen(self.setup_manager.initial_screen)

        # init controller manager
        self.controller_manager = ControllerManager(screens)                                      screens

        # load synth data (synth manager???)
        self.synth_manager = SynthManager()
        self.synth_manager.load_synths(self.controller_manager.synths)

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
        callbacks to bind to controller events."""
        self._check_synths()
        self.controller_manager.initialise_controllers(
            self.synth_manager.options_lists
            self.midi.send_nrpn,
            self.patch_manager.on_load_unconfirmed
        )

        #self.ui.simple_popup("Welcome", "Synth Controller")


    # channel setup #
    def _check_synths(self):
        """checks if synths found in screens are registered in setttings file,
        if so set controller channels else runs midi channel selection popup"""
        synth_missing = False
        channels = {}
        for synth in self.synths:
            if synth not in self.setup_manager.channels:
                channels[synth] = None
                synth_missing = True
            else:
                channels[synth] = self.setup_manager.channels[synth]

        if synth_missing:
            self.ui.channel_selection_popup(channels)
        else:
            self.controller_manager.set_channels(channels)

    def _on_channel_selection(self, _, data):
        """apply the midi channel selection to setup manager and set
        controller channels"""
        self.setup_manager.channels = data
        self.controller_manager.set_channels(data)


    # midi callbacks #    
    def on_incoming_cc(self, channel, nrpn, value):
        """Set and display controller value from incoming midi"""
        self.controller_manager.set_controller_value(channel, nrpn, value)
        
    def on_incoming_sysex(self, message):
        """Parse incoming sysex message"""
        patch_manager.parse_sysex(message)

    
    # error callbacks # create a logging object instead???
    def on_no_patch_details_error(self):
        """display error message for synth without patch details"""
        print(NO_PATCH_DETAILS)


    # functions to be moved to patch_manager class: #
    def _on_dump(self, synth):
        """send midi cc from every controller of given synth"""
        self.controller_manager.send_all(synth)

    def _on_recieve(self, synth):
        """send dump request sysex over midi"""
        self.midi.send_sysex(self.synths[synth]['dump request command'])
 
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
