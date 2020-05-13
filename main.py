#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2017 tom <tom@crunchbang>
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
  
import os
import struct

import alsaseq

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty,\
                            BooleanProperty, ObjectProperty,\
                            BoundedNumericProperty
                            #OptionProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.clock import Clock
#from kivy.factory import Factory

VERBOSE = True

notes = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')

# Unique to mopho: 
options = {'glide': ('Fixed rate', 'Fixed rate auto', 'Fixed time', 
                     'Fixed time auto'
                     ),
           'key_assign': ('Low Note', 'Low Note, re-trigger', 'High Note',
                          'High Note, re-triggger', 'Last Note', 
                          'Last Note, re-triggger'
                          ),
           'destinations': ('Off', 'Osc 1 Freq', 'Osc 2 Freq', 
                            'Osc 1 and 2 Freq', 'Osc Mix', 'Noise Level',
                            'Osc 1 Pulse Width', 'Osc 2 Pulse Width', 
                            'Osc 1 and 2 Pulse Width', 'Filter Frequency',
                            'Resonance', 'Filter Audio Mod Amt', 'VCA Level',
                            'Pan Spread', 'LFO 1 Freq', 'LFO 2 Freq', 
                            'LFO 3 Freq', 'LFO 4 Freq', 'All LFO Freq', 
                            'LFO 1 Amt', 'LFO 2 Amt', 'LFO 3 Amt', 'LFO 4 Amt',
                            'All LFO Amt', 'Filter Env Amt', 'Amp Env Amt',
                            'Env 3 Amt', 'All Env Amounts', 'Env 1 Attack', 
                            'Env 2 Attack', 'Env 3 Attack', 'All Env Attacks', 
                            'Env 1 Decay', 'Env 2 Decay', 'Env 3 Decay',
                            'All Env Decays', 'Env 1 Release', 'Env 2 Release',
                            'Env 3 Release', 'All Env Releases', 'Mod 1 Amt', 
                            'Mod 2 Amt', 'Mod 3 Amt', 'Mod 4 Amt', 
                            'External Audio In Level', 'Sub Osc 1 Level', 
                            'Sub Osc 2 Level'
                            ),
           'time_syncs': ('32 Step', '16 Step', '8 Step', '6 Step', '4 Step', 
                          '3 Step', '2 Step', '1.5 Step', '1 Step', 
                          '2/3 Steps', '1/2 Step', '1/3 Steps', '1/4 Step', 
                          '1/6 Step', '1/8 Step', '1/16 Step'
                          ),
           'lfo_shapes': ('Triangle', 'Rev. Saw.', 'Sawtooth', 'Square', 
                          'Random'
                          ),
           'sources': ('Off', 'Sequence Track 1', 'Sequence Track 2', 
                       'Sequence Track 3', 'Sequence Track 4', 'LFO 1', 
                       'LFO 2', 'LFO 3', 'LFO 4', 'Filter Envelope', 
                       'Amp Envelope', 'Envelope 3', 'Pitch Bend', 'Mod Wheel',
                       'Pressure', 'MIDI Breath', 'MIDI Foot', 
                       'MIDI Expression', 'Velocity', 'Note Number', 'Noise', 
                       'Audio In Envelope Follower', 'Audio In Peak Hold'
                       )
           }
                      
nrpn_numbers = (0, 1, 2, 3, 4, 114, 5, 6, 7, 8, 9, 115, 10, 11, 12, 93, 96, 13,
                14, 116, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 
                30, 31, 32, 33, 34, 35, 36, 29, 37, 38, 39, 40, 41, 42, 43, 44,
                45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
                60, 61, 62, 63, 64, 98, 65, 66, 67, 68, 69, 70, 71, 72, 73,
                74, 75, 76, 81, 82
                )





class MainScreen(BoxLayout):
    """The main screen."""
    
    def send_program(self):
        """Sends value for every main controller."""
        for controller in main_controllers:
            controller.send_midi_cc()
    
    def request_edit_buffer(self): # not working, manually request from synth
        """Sends request edit buffer sys ex message"""
        
        print ("sending sysex")
        # unique to mopho:
        midi_event = (130, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                      "\xF0\x01\x25\x06\xF7")
        alsaseq.sysex(midi_event)

class BaseController(BoxLayout):
    """Controller base class
    
       A controller controls a parameter of the synth.
       A controller always has a name, nrpn number and a value.
       The nrpn is how it is referenced by the synth.
       How it's value is displayed and edited depends on its sub-class,
       i.e. slider
       
       It's value may be bounded by a minimum and a maximum.
       
       Offset is used if the value does not corespond to the midi value to be 
       sent. i.e. a contoller that can have a negative value.
       
       If multiple controllers control the same parameter, one will be the main
       controller and the rest will be sub-controllers, only the main 
       controller will send midi, a sub-controller must do it through the main 
       controller.
       
       A controller's midi output is paused when recieving to stop repetition
       of the changes. 
       """ 
    name = StringProperty("")
    nrpn_number = NumericProperty(0)
    value = NumericProperty(0)
    minimum = NumericProperty(0)
    maximum = NumericProperty(127)
    offset = NumericProperty(0)
    is_sub_controller = BooleanProperty(False)
    display_function = ObjectProperty(lambda value: str(value))
    
    def __init__(self, **kwargs):
        super(BaseController, self).__init__(**kwargs)
        controllers.append(self)
        self.pause_midi = False
        self.bind(on_value=self.on_value)

    def on_value(self, x , y):
        """Responds to a change in controller value.
        
           Sends controller value if midi is not paused. 
           Displays chosen value if approriate for controller.
           Arguments x and y are ignored.
           """
        print (self, self.is_sub_controller)
        if self.is_sub_controller:
            return
        if self.pause_midi:
            self.pause_midi = False
        else:
            self.send_midi_cc()
        if type(self) in (ToggleController, SwitchController, \
                            DropDownController):
            self.display_selected()
            
    def send_midi_cc(self):
        """Constructs and sends control change midi message"""
        value = self.value + self.offset
        midi_event = []
        
        # (type, flags, tag, queue, time stamp, source, destination, data)
        midi_event.append((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                           (0, 0, 0, 0, 0x63, self.nrpn_number >> 7 & 0x7F)
                           )
                          )
        midi_event.append((10, 1, 0, 253, (0, 0), (0, 0), (0,0),
                           (0, 0, 0, 0, 0x62, self.nrpn_number & 0x7F)
                           )
                          )
        midi_event.append((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                           (0, 0, 0, 0, 0x06, value >> 7 & 0x7F)
                           )
                          )
        midi_event.append((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                           (0, 0, 0, 0, 0x26, value & 0x7F)
                           )
                          )
        for line in midi_event:
            alsaseq.output(line)
        if VERBOSE:
            print ("sent", self)
        
    def loaded(self, value):
        """Controller's value is set as loaded from file."""
        self.pause_midi = True
        self.value = value
        if VERBOSE:
            print ("loaded", self) 
        
    def recieved_midi(self, value):
        """Controller's value is set as recieved from synth."""
        self.pause_midi = True
        self.value = value - self.offset
        if VERBOSE:
            print ("recieved", self)      
    
    # sort this out done??
    #def change_controller_value(self, name, value):
    #    #print name, value
    #    for controller in controllers:
    #        try:
    #            if controller.name == name:
    #                controller.recieved_midi(value)
    #        except AttributeError:
    #            pass

    def display_selected(self):
        """Highlight selected value for appropriate controller types."""    
        for child in [c for c in self.children if isinstance(c, Button)]:
            child.state = 'down' if self.value in child.values else 'normal'
    
    def notes(self, value):
        """Returns value as musical note."""
        #print value
        return notes[value%12] + str(value/12)
    
    def __repr__(self):
        return "<{}>:{} {}".format(self.nrpn_number, self.name, self.value)


class SlideController(BaseController):
    """A slider type controller.
    
       The value is changed by moving the slider.
       Can be horizontal or vertical.
       """
    pass


class SwitchController(BaseController):
    """A switch type controller.
    
       The value is changed by clicking/touching the appropriate button.
       """
    pass

    
class ToggleController(BaseController):
    """A toggle switch type controller.
    
       A modal type controller, switched on or off by a click/single touch."""
    pass


class TouchController(BaseController):
    """A touch type controller.
    
       The value is changed by a touch/click then draging up or down, or 
       mouse scrolling over controller"""
       
    def __init__(self, **kwargs):
        super(TouchController, self).__init__(**kwargs)
        self.bind(on_touch_down=self.on_down)       
        self.bind(on_touch_move=self.on_move)
        self.bind(on_touch_up=self.on_up)

    def on_down(self, wid, touch):
        """Grabs touch event if click/touch is over controller."""
        if touch.x >= self.x and touch.x <= self.x + self.size[0] and\
           touch.y >= self.y and touch.y <= self.y + self.size[1]:
            # touch belongs to this controller, proceed
            touch.grab(self)
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    self.value = self.bound_check(self.value + 1)
                elif touch.button == 'scrollup':
                    self.value = self.bound_check(self.value - 1)
        
    def on_move(self, wid, touch):
        """Changes controllers value coresponding to move after click/touch."""
        if touch.grab_current is self:
            self.value = self.bound_check(int(self.value + touch.dy))    

     
    def on_up(self, wid, touch):
        """Releases 'grab' of touch event on click/touch up."""
        if touch.grab_current is self:
            touch.ungrab(self)
    
    def bound_check(self, value):
        """Makes sure value stays within bounds and returns it."""
        if self.minimum <= value <= self.maximum:
            return value
        return self.maximum if value > self.maximum else self.minimum


class DropDownController(BaseController):
    """A drop down type controller.
    
       The value is selected from a drop down list. """
    option_list = StringProperty('')
    always_on = BooleanProperty(False)
    
    def setup(self, value):
        """Creates the drop down list for the controller."""
        self.dropdown = DropDown()
        self.options = options[self.option_list]
        self.button = [widget for widget in self.children 
                       if isinstance(widget, Button)
                       ][0]
        for option in self.options:
            btn = Button(text=option, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self.select_option)
        self.display_selected()

    def select_option(self, i, option):
        """Sets controller value to chosen option."""
        self.value = self.options.index(option)
        
    def display_selected(self):
        """Displays chosen option."""
        self.button.text = self.options[self.value]
        if self.options[self.value] == 'Off':
            self.button.state = 'normal'
        else:
            self.button.state = 'down'
    

class MyApp(App):
    """The main application"""
    def on_start(self):
        """Controller initialisation.
        
           Calls setup for all drop down controllers.
           Creates list of main controllers in order as they are dumped from
           synth.
           """
        for controller in controllers:
            if isinstance(controller, DropDownController):
                controller.setup(0)
        global main_controllers
        main_controllers = []
        for nrpn in nrpn_numbers:
            main_controllers.append([c for c in controllers if
                                    not c.is_sub_controller
                                    and c.nrpn_number == nrpn][0])
                                    
    def build(self):
        """Builds the main screen from kv file and returns it to kivy."""
        return MainScreen()


def check_midi(dt):
    """Recieves incoming midi"""
    if alsaseq.inputpending():
        event = alsaseq.input()
        if event[0] == 10:
            control_change(event)
        elif event[0] == 130:
            sys_ex(event)


def control_change(event):
    """Recieves control change midi event.
    
       Sets relevent contoller value.
       """ 
    cc_data = [event[-1][-1]]
    while len(cc_data) < 4:
        event = alsaseq.input()
        cc_data.append(event[-1][-1])
    nrpn = cc_data[0] << 7 | cc_data[1]
    value = cc_data[2] << 7 | cc_data[3]
    [c.recieved_midi(value) for c in main_controllers if c.nrpn_number == nrpn]


def sys_ex(event):
    """Recieves system exclusive midi event.
    
       Recieves data in two chunks.
       Strips packing bytes.
       Sets values for all relevent controllers.
       """
    # unique to mopho: needs fixing
    program_dump = True if event[-1][-1][3] == '\x02' else False
    first_data = event[-1][-1][6 if program_dump else 4:]
    event = alsaseq.input()
    second_data = event[-1][-1][6 if program_dump else 4:]
    packed_data = map(ord, first_data + second_data)
    unpacked_data = []
    for i, data in enumerate(packed_data):
        if i % 8 == 0:
            packing_byte = data
        else:
            unpacked_data.append(128 + data if packing_byte & (1 << ((i%8)-1)) else data)

    #for i in (i for i in range(len(packed_data)) if i % 8):
    #    unpacked_data.append(packed_data[i]) 
    for param, value in enumerate(unpacked_data):
        #print param, value
        try:
            main_controllers[param].recieved_midi(value)
        except IndexError:
            pass
        

def main():
    alsaseq.client('Mopho control', 1, 1, False)
    #alsaseq.connectfrom(0, 28, 0)
    #alsaseq.connectto(1, 28, 0)

    global controllers
    controllers = []
    #last_cc_recieved = None
    clock = Clock.schedule_interval(check_midi, 0.01)
    MyApp().run()
    
    
if __name__ == '__main__':
    main()
