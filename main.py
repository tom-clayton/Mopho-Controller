#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2020 tom clayton <clayton_tom@yahoo.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
  
from kivy.config import Config
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 400)
Config.set('graphics', 'top',  100)
Config.set('graphics', 'width',  1200)
Config.set('graphics', 'height',  800)
from kivy.app import App


# Remove not needed imports:

from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.actionbar import ActionBar
from kivy.clock import Clock
from kivy.lang import Builder

import controller_manager
import midi_interface
import file_manager


import Mopho # Eventually make this import programatically depending on 
             # the synth or synths being controlled.

Builder.load_file('Mopho.kv') # And this kivy file load

class MainScreen(BoxLayout):
    """The main screen."""
    def __init__(self, midi, file_manager, controllers, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.midi = midi
        self.file_manager = file_manager
        self.controllers = controllers
    
    # Move these when action bar created:
    def save_program(self):
        self.file_manager.show_save_popup()
    
    def load_program(self):
        self.file_manager.show_load_popup()
    
    def request_current_program(self):
        self.midi.request_current_program()
        
    def send_current_program(self):
        self.controllers.send_program()
    

class MainApp(App):
    """The main application"""
    synth = Mopho.Synth() # see note by import
    controllers = controller_manager.ControllerManager()
    midi = midi_interface.Midi(synth, controllers)
    file_manager = file_manager.FileManager(controllers)

    clock = Clock.schedule_interval(midi.check_midi, 0.01)
    
    def on_start(self):
        """Controller initialisation."""
        self.controllers.setup_controllers(self.midi, self.synth)
                                    
    def build(self):
        """Builds the main screen from kv file and returns it to kivy."""
        return MainScreen(self.midi, self.file_manager, self.controllers)

def main():
    app = MainApp()
    app.run()
    
    
if __name__ == '__main__':
    main()
