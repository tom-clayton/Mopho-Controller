
from ui import MainScreen
from setup_manager import SetupManager, NoSetupException
from controller_manager import ControllerManager
from synth_manager import SynthManager
#from midi_test import Midi
from midi import Midi
from error_handler import ErrorHandler
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

        # build screens
        self.setup_manager.build_screens()

        # init controller manager
        self.controller_manager = ControllerManager(self.ui.screens)

        # init synth manager
        self.synth_manager = SynthManager(self.controller_manager.synths)

        # init midi interface
        self.midi = Midi()

        # init error handler
        self.error_handler = ErrorHandler()

        # init patch manager
        self.patch_manager = PatchManager(
                                self.midi,
                                self.ui,
                                self.controller_manager,
                                self.synth_manager,
                                self.error_handler
                            )

        # set midi callbacks
        self.midi.set_callbacks(
            self.controller_manager.set_controller_value,
            self.patch_manager.parse_sysex
        )

    def build(self):
        """build the kivy app"""
        return self.ui

    def on_start(self):
        """Initialise controllers with synth options lists and midi and patch
        objects for callbacks to bind to controller events.
        Assign and set midi channels.""" 
        self.controller_manager.initialise_controllers(
            self.synth_manager.options_lists,
            self.midi,
            self.patch_manager
        )
        
        self.setup_manager.assign_channels(self.controller_manager.synths)
        self.controller_manager.set_channels(self.setup_manager.channels)
        self.synth_manager.set_channels(self.setup_manager.channels)

        #self.ui.simple_popup(WELCOME_TITLE, WELCOME_MESSAGE)


def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
    main()    
