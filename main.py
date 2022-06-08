
from setup_manager import SetupManager, NoSetupException
from midi_empty import Midi
from controller_manager import ControllerManager
from ui import MainScreen
from synth_data import SynthDataLoader
from strings import *

from kivy.app import App
from kivy.core.window import Window

import json
import os
import sys
import time


class MainApp(App):
    """Comunicates between ui, midi interface and setup manager,
    Controls file i/o"""
    def __init__(self, **kwargs):
        """create singletons, bind events"""
        super(MainApp, self).__init__(**kwargs)

        Window.size = (1200, 800)
        #Window.size = (400, 400)

        # setup manager
        try:
            self.setup_manager = SetupManager()
        except NoSetupException:
            print("no setup")
            sys.exit(1)
            # eventually run as patch librarian if no setup is found.

        # ui
        self.ui = MainScreen()
        screens = self.ui.build_screens(self.setup_manager.screens)
        self.ui.set_screen(self.setup_manager.initial_screen)

        # controller manager
        self.controller_manager = ControllerManager(self, screens)

        # synth data
        self.synth_data_loader = SynthDataLoader()
        self.synths = self.synth_data_loader.load(
                                self.controller_manager.synths
                            )
        self.controller_manager.add_synth_data(self.synths)

        # midi interface
        self.midi = Midi(self.on_midi_cc, self.on_midi_sysex)

        # events
        self.ui.bind(on_load_unconfirmed=self._on_load_unconfirmed)
        self.ui.bind(on_save_unconfirmed=self._on_save_unconfirmed)
        self.ui.bind(on_load_confirmed=self._on_load)
        self.ui.bind(on_save_confirmed=self._on_save)
        self.ui.bind(on_channel_selection=self._on_channel_selection)  

    def build(self):
        """build the kivy app"""
        return self.ui

    def on_start(self):
        """check if synths have a midi channel registered in settings file.
        initialise controllers."""
        self._check_synths()
        self.controller_manager.initialise_controllers() # pass synth data objects
        #self.ui.simple_popup("Welcome", "Synth Controller")

    # channels #
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
        """apply the midi selection to setup manager and set controller
    channels"""
        self.setup_manager.channels = data
        self.controller_manager.set_channels(data)

    # midi #    
    def on_ui_cc(self, channel, nrpn, value):
        """send nrpn change midi message"""
        self.midi.send_nrpn(channel, nrpn, value)
        
    def on_midi_cc(self, channel, nrpn, value):
        """set controller value in ui display"""
        self.controller_manager.set_controller_value(channel, nrpn, value)
        
    def on_midi_sysex(self, message):
        # deal with message
        pass

    def _on_dump(self, synth):
        """send midi cc from every controller of given synth"""
        self.controller_manager.send_all(synth)

    def _on_recieve(self, synth):
        """send dump request sysex over midi"""
        self.midi.send_sysex(self.synths[synth]['dump request command'])

    # files #
    def _on_load_unconfirmed(self, _, data):
        """open a confirm popup to confirm patch load"""
        self.ui.confirm_popup(CONFIRM_LOAD, 'on_load_confirmed', data)
        print("load...")
    
    def _on_load(self, _, data):
        """load data from file, add nrpns according to dump order,
        send to controllers for given synth"""
        synth, filename = data
        print("load", synth, filename)
        return
        with open(filename, "rb") as fo:
            data = fo.read()
        self.controller_manager.set_controller_values(
                                    synth,
                                    self.synths[synth].nrpn_order,
                                    data
                                )
    def _on_save_unconfirmed(self, _, data):
        """open a confirm popup to confirm patch save if file alreadey exists
    else save file"""
        synth, filename = data
        if os.path.exists(data[1]):
            self.ui.confirm_popup(CONFIRM_SAVE, 'on_save_confirmed', data)
        else:
            self.on_save(None, data)
        
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


    # test #
    def run_test(self):
        """test midi input"""
        self.controller_manager.set_controller_value('mp', 42, 162)


def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
    main()    
