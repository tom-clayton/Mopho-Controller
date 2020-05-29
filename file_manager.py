#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  file_manager.py
#  
#  Copyright 2020 tom <tom@MusicPC>
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

from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder

import os

Builder.load_file('file_manager.kv')

class FileManager():
    
    def __init__(self, client):
        self.client = client
            
    def show_save_popup(self):
        """Displays save pop-up dialogue."""
        content = SaveDialog(save=self.check_overwrite, 
                               cancel=self.dismiss_save_popup)
        self.save_popup = Popup(title="Save file", content=content,
                                size_hint=(0.9, 0.9))
        self.save_popup.open()

    def show_load_popup(self):
        """Displays load pop-up dialogue."""
        content = LoadDialog(load=self.load_program, 
                               cancel=self.dismiss_load_popup)
        self.load_popup = Popup(title="Load file", content=content,
                                size_hint=(0.9, 0.9))
        self.load_popup.open()
    
    def show_save_popup(self):
        """Displays save pop-up dialogue."""
        content = SaveDialog(save=self.check_overwrite, 
                               cancel=self.dismiss_save_popup)
        self.save_popup = Popup(title="Save file", content=content,
                                size_hint=(0.9, 0.9)
                                )
        self.save_popup.open()
    
    def check_overwrite(self, path, filename):
        """Checks whether to overwite an existing file."""
        full_filename = os.path.join(path, filename)
        print ("check", full_filename)
        if os.path.isfile(full_filename):
            content = ConfirmDialog(message='File exists. Are you sure?',
                                      data=full_filename,
                                      confirm=self.save_program,
                                      cancel=self.dismiss_confirm_popup)
            self.confirm_popup = Popup(title="Confirm", content=content,
                                       size_hint=(0.9, 0.9))
            self.confirm_popup.open()
        else:
            self.save_program(full_filename)
        self.dismiss_save_popup()    
    
    def load_program(self, path, filename):
        """Loads binary data from file."""
        full_filename = os.path.join(path, filename[0])
        print ("loading ", full_filename)
        with open(full_filename, 'rb') as fo:
            self.client.set_load_data(fo.read())
        self.dismiss_load_popup()
            
    def save_program(self, filename):
        """Saves binary data to file."""
        print ("saving ", filename)
        with open(filename, 'wb') as fo:
            fo.write(bytearray(self.client.get_save_data()))
        self.dismiss_confirm_popup()
    
    def dismiss_load_popup(self):
        """Removes load pop-up dialogue."""
        self.load_popup.dismiss()
        
    def dismiss_save_popup(self):
        """Removes save pop-up dialogue."""
        self.save_popup.dismiss()
        
    def dismiss_confirm_popup(self):
        """Removes confirm pop-up dialogue."""
        self.confirm_popup.dismiss()

class LoadDialog(FloatLayout):
    """Load pop-up dialogue."""
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    """Save pop-up dialogue."""
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ConfirmDialog(FloatLayout):
    """Confirm pop-up dialogue"""
    message = StringProperty(None)
    data = ObjectProperty(None)
    confirm = ObjectProperty(None)
    cancel = ObjectProperty(None)

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
