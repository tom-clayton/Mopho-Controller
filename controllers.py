#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  conroller_manager.py
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
from kivy.properties import NumericProperty, StringProperty,\
                            BooleanProperty, ObjectProperty,\
                            BoundedNumericProperty
                            #OptionProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior

from kivy.lang import Builder

Builder.load_file('controllers.kv')

# raw_controllers is only global so classes created by kv file can
# register themselves. mopho.controllers should be used to access
# them. (Maybe they can be registered by looking them up using the 
# kivy api in mopho.on_start() instead?)
# global raw_controllers 
raw_controllers = [] 

class ControllerManager():
    def setup_controllers(self, midi, synth):
        """Creates list of main controllers.
           Passes midi object to all controllers.
           Sets up option lists for drop down controllers.
           Creates 
           Gets order of parameters.
        """
        self.synth = synth
        self.controllers = []
        for controller in raw_controllers:
            if not controller.is_sub_controller:
                self.controllers.append(controller)
                controller.midi = midi
            controller.synth = synth
            if isinstance(controller, DropDownController):
                controller.setup(0)
        
        # Could this be setup on init as a list of 
        # kivy properties, so they automatically update for loading
        # and saving, etc ??        
        self.controller_values = tuple([0 for x in range(
                                    self.synth.number_of_parameters)])
                                    
        if hasattr(self.synth, 'nrpn_order'):
            self.nrpn_order = self.synth.nrpn_order
        else:
            self.nrpn_order = range(self.synth.number_of_parameters)
            
    
    def set_controller_value(self, nrpn, value):
        """Sets relevant controllers value"""
        try:
            controller = self.controller_from_nrpn(nrpn)
            controller.set_value(value)
        except IndexError:
            pass

    def set_all_values(self, values):
        """Sets all controllers values from tuple of values in order
           they come from a program dump.
           Saves a reference to tuple so the app can load, save and 
           upload parameter values which are not controlled by the app.
           """
        
        # see note in setup_controllers method   
        self.controller_values = values

        for i, nrpn in enumerate(self.nrpn_order):
            if nrpn is not None:
                self.set_controller_value(nrpn, values[i])
        
    
    def send_program(self):
        """Sends value for every main controller."""
        for controller in self.controllers:
            controller.send_cc()
    
    def get_all_values(self):
        """Returns a tuple of all synth parameter values, including 
           ones not controlled by a controller."""
        
        # see note in setup_controllers method 
        output = []   
        for i, nrpn in enumerate(self.nrpn_order):
            try:
                output.append(self.controller_from_nrpn(nrpn)\
                                .get_value())
            except IndexError:
                output.append(self.controller_values[i])
        
        return output
                
    def controller_from_nrpn(self, nrpn):
        """Returns controller with given nrpn number.
           Will give IndexError if there isn't one."""
        controllers_found =  [c for c in self.controllers \
                                    if c.nrpn == nrpn]
                                
        if len(controllers_found) > 1:
            print ("Warning: Multiple top level controllers found for nrpn",
                    nrpn)
            print ("Using: ", controllers_found[0])
            for controller in controllers_found[1:]:
                print("Ignoring: ", controller)

        return controllers_found[0] 

class BaseController(BoxLayout):
    """Controller base class
       
       A controller controls a parameter of the synth.
       
       If multiple controllers control the same parameter, one will be 
       the main controller and the rest will be sub-controllers, only 
       the main controller will send midi, a sub-controller must do it 
       through the main controller.
       
       The nrpn is how it is referenced by the synth.
       How it's value is displayed depends on its sub-class, i.e. slider.
       
       It's value is bounded by a minimum and a maximum.
       
       Offset is for when the value does not corespond to the value 
       to be sent. i.e. a controller that can have a negative value.
       
       Controller objects are created by the kv file.
       """ 
    
    # Default controller properties. Set by kv file if required:
    name = StringProperty("")
    nrpn = NumericProperty(0)
    value = NumericProperty(0)
    minimum = NumericProperty(0)
    maximum = NumericProperty(127)
    offset = NumericProperty(0)
    is_sub_controller = BooleanProperty(False)
    display_function = ObjectProperty(lambda value: str(value))
    
    def __init__(self, **kwargs):
        super(BaseController, self).__init__(**kwargs)
        raw_controllers.append(self)
        self.bind(on_value=self.on_value)

    def on_value(self, *args):
        """Responds to a change in controller value.
        
           Displays chosen value if approriate for controller.
           Sends out value over midi.
           """
	
        if type(self) in (ToggleController, SwitchController,
                            DropDownController):
            self.display_selected()
        
        # Only send midi if it is a main_controller:
        if self.is_sub_controller:
            return
            
        self.send_cc()

        # Remember the prev value to check if value
        # only changes by one, allowing the use of more efficient midi
        # messaging available in some synths.
        self.prev_value = self.value
    
    def send_cc(self):
        """Sends out the contollers value over midi"""
        self.midi.send_cc(self.nrpn, self.get_value())

    def get_value(self):
        """Gets controller's value with offset removed."""
        return self.value - self.offset
        
    def set_value(self, value): 
        """Sets controller's value."""
        self.value = value + self.offset    

    def display_selected(self):
        """Highlight selected value for appropriate controller types."""    
        for child in [c for c in self.children if isinstance(c, Button)]:
            child.state = 'down' if self.value in child.values else 'normal'
    
    def note(self, value):
        """Returns value as musical note."""
        notes = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 
                 'A#', 'B')
        return notes[value%12] + str(value//12)
    
    def __repr__(self):
        return "<{}>:{} {}".format(self.nrpn, self.name, self.value)

# Sub-classes for controller objects created in kv file:
class SlideController(BaseController):
    """A slider type controller.
    
       The value is changed by moving the slider.
       Can be horizontal or vertical.
       """
    pass


class SwitchController(BaseController):
    """A switch type controaller.
    
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
        self.options = self.synth.options[self.option_list]
        self.button = [widget for widget in self.children 
                       if isinstance(widget, Button)][0]
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
            
def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
