
from setup_manager import SetupManager, NoSetupException
from midi_empty import Midi
from controller_manager import ControllerManager
from ui import MainScreen
from error import ErrorHandler
from strings import *

from kivy.app import App

import json
import os
import sys


class MainApp(App):
    """Comunicates between ui, midi interface and setup manager,
    Controls file i/o"""
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        try:
            self.setup_manager = SetupManager()
        except NoSetupException:
            print("no setup")
            sys.exit(1)
            # eventually run as patch librarian, when no setup is found.

        self.ui = MainScreen()
        screens = self.ui.build_screens(self.setup_manager.screens)
        self.controller_manager = ControllerManager(self, screens)
        
        self.midi = Midi(self.on_midi_cc, self.on_midi_sysex)
        self.ui.bind(on_load_unconfirmed=self.on_load_unconfirmed)
        self.ui.bind(on_save_unconfirmed=self.on_save_unconfirmed)
        self.ui.bind(on_load_confirmed=self.on_load)
        self.ui.bind(on_save_confirmed=self.on_save)
        self.ui.bind(on_channel_selection=self.on_channel_selection)
        self.error_handler = ErrorHandler()
        self.ui.set_screen(self.setup_manager.initial_screen)
        self.synths = self.controller_manager.synths

    # kivy #
    def build(self):
        """build the kivy app"""
        return self.ui

    def on_start(self):
        """check if synths have a midi channel registered in settings file.
        initialise controllers."""
        self._check_synths(self.synths)
        self.controller_manager.initialise_controllers() # pass synth data objects
        #self.ui.simple_popup("Welcome", "Synth Controller")
  
    def _check_synths(self, synths):
        """checks if synths found in screens are registered in setttings file,
        if so sets controller channels else runs midi channel selection popup"""
        for synth in synth:
            if synth not in self.setup_manager.synth_channels:
                self.ui.channel_selection_popup(self.synths)
                return
            else:
                self.controller_manager.set_channels(self.setup_manager.channels)

    def on_channel_selection(self, _, data):
        """apply the midi selection to setup manager and set controller
    channels"""
        self.setup_manager.channels = data
        self.controller_manager.set_channels(data)
    
    def _load_synth_data(self):
        """load the synth related data for each synth in the settings file""" 
        self.synth_data = {}
        
        for synth in self.synths:
            if synth and synth != 'default':
                try:
                    with open(f"synths/{synth}.json") as fo:
                        self.synth_data[synth] = json.load(fo)
                except FileNotFoundError:
                    print("no synth data")# use error handler     
            
    #def get_option_list(self, synth, option_list):
    #    """return requested list of options from synth data file"""
    #    return self.synth_data[synth]['options'][option_list]

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

    def on_dump(self, synth):
        """send midi cc from every controller of given synth"""
        self.controller_manager.send_all(synth)

    def on_recieve(self, synth):
        """send dump request sysex over midi"""
        self.midi.send_sysex(self.synths[synth]['dump request command'])

    # files #
    def on_load_unconfirmed(self, _, data):
        """open a confirm popup to confirm patch load"""
        self.ui.confirm_popup(CONFIRM_LOAD, 'on_load_confirmed', data)
        print("load...")
    
    def on_load(self, _, data):
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
    def on_save_unconfirmed(self, _, data):
        """open a confirm popup to confirm patch save if file alreadey exists
    else save file"""
        synth, filename = data
        if os.path.exists(data[1]):
            self.ui.confirm_popup(CONFIRM_SAVE, 'on_save_confirmed', data)
        else:
            self.on_save(None, data)
        
    def on_save(self, _, data):
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

    def error(self, name, data):
        """pass error to handler"""
        self.error_handler.error(name, data)

    def run_test(self):
        """test midi input"""
        self.controller_manager.set_controller_value('test', 2, 20)

def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
    main()    
