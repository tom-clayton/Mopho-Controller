#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  conrollers.py
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
from kivy import factory
from kivy.lang import Builder

Builder.load_file('controllers.kv')

# raw_controllers is only global so classes created by kv file can
# register themselves. mopho.controllers should be used to access
# them. (Maybe they can be registered by looking them up using the 
# kivy api in mopho.on_start() instead?)
# global raw_controllers 
all_controllers = [] 


class ControllerManager():
    def setup_controllers(self, midi, synth):
        """Creates list of main controllers.
           Calls setup for controllers that need it.
           Passes midi object to all main controllers."""
        self.synth = synth
        
        for controller in all_controllers:
            controller.synth = synth   
            controller.setup()
            
        self.controllers = [c for c in all_controllers if not \
                                c.is_subcontroller]    
        self.sub_controllers = [c for c in all_controllers if \
                                c.is_subcontroller]
       
        for controller in all_controllers:
            controller.display_selected()
            
        for controller in self.controllers:
            controller.midi = midi
            
        
        # Load not working!
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
        #print(self.controller_values)
        #self.print_all_controllers()

    def send_program(self):
        """Sends value for every main controller."""
        for controller in self.controllers:
            controller.send_cc()
            
    def get_save_data(self):
        """Returns a bytearray of all synth parameter values, including 
           ones not controlled by a controller."""
        
        # see note in setup_controllers method 
        output = []   
        for i, nrpn in enumerate(self.nrpn_order):
            try:
                output.append(self.controller_from_nrpn(nrpn)\
                                .get_value())
            except IndexError:
                output.append(self.controller_values[i])
        
        return bytearray(output)
    
    def set_load_data(self, data):
        """Receives load data from file manager."""
        data = [x for x in fo.read()]
        self.set_all_values(data)
                
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

    def print_all_controllers(self):
        """Prints the value of every controller to stdout."""
        for controller in self.controllers:
            print (controller)

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
    is_subcontroller = BooleanProperty(False)
    display_function = ObjectProperty(lambda value: str(value))
    
    def __init__(self, **kwargs):
        super(BaseController, self).__init__(**kwargs)
        all_controllers.append(self)
        self.bind(on_value=self.on_value) # put in kivy file??

    def setup(self):
        """Called once at startup. 
           Over-ridden by sub classes."""
        pass
        
    def display_selected(self):
        """Called when contoller selection should be displayed to
           screen.
           Over-ridden by sub classes."""
        pass
    
    def on_value(self, *args):
        """Responds to a change in controller value.
        
           Checks for subcontroller.
           Displays chosen value if approriate for controller.
           Sends out value over midi.
           """
        

        if self.is_subcontroller:
            self.parent.on_subcontroller_value(self)
            return
        
        try:
            self.on_dualcontroller_value()
        except AttributeError:
            pass
        
        try:
            self.display_selected()
        except AttributeError:
            pass

        print("CC:", self)

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
    
    def value_in_midirange(self, value):
        """Checks if controllers value lies within
           its allowed midi value range.
           This is for sub-controllers, which only represent part of the
           range of midi values of their parent dual-controller."""
        
        #print ("vim", self)
        #print (value, self.midirange)
        if self.midirange[0] <= value <= self.midirange[1]:
            #print(True)
            return True
        else:
            #print(False)
            return False
            
    def note(self, value):
        """Returns value as musical note."""
        notes = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 
                 'A#', 'B')
        return notes[value%12] + str(value//12)
    
    def __repr__(self):
        return f"{type(self)}<{self.nrpn}>:{self.name} {self.value}"

# Sub-classes for controller objects created in kv file:
class SlideController(BaseController):
    """A slider type controller.
    
       The value is changed by moving the slider.
       Can be horizontal or vertical.
       """ 
    pass
    
class ToggleController(BaseController):
    """A toggle button type controller.
    
       A binary type controller, switched on or off by a click/single 
       touch."""
    pass

class RadioController(BaseController):
    """A radio switch type conntroller.
    
       The controller made up of multiple radio buttons, where each 
       one represents a value or values of the controller."""
    
    def setup(self):
        """Setup controller.
        
           Makes list of buttons.
           Displays controller."""
        self.buttons = [c for c in self.children \
                            if isinstance(c, RadioButton)]
        
        for button in self.buttons:
            if button.all_other_values is True:
                self.all_other_values_btn = button

    def display_selected(self):
        """Displays which button is selected for controller."""
            
        for button in self.buttons:
            if not button.all_other_values and \
                            self.value == button.value:
                button.state = 'down'
            else:
                button.state = 'normal'
        
        if self.is_subcontroller and \
                    not self.value_in_midirange(self.value):
            self.all_other_values_btn.state = 'down'

class RadioButton(ToggleButton):
    """A radio button.
    
       Only one radio button in a controller can be selected at any
       time."""
    def on_press(self):
        """Radio button pressed.
        
           Sets value of radio-controller or runs other values button 
           function in dual controller if it is such a button"""
        if self.all_other_values:
            self.parent.parent.on_all_other_values_option_selected()
        else:
            self.parent.value = self.value
            

class TouchController(BaseController): # rename swipe
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
    # always_on = BooleanProperty(False) # ??
    
    def setup(self):
        """Creates the drop down list for the controller."""
        self.dropdown = DropDown()
        self.options = self.synth.options[self.option_list]
        self.main_button = [widget for widget in self.children 
                       if isinstance(widget, Button)][0]

        for option in self.options:
            btn = Button(text=option, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
            
        self.main_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self.select_option)

    def select_option(self, i, option):
        """Sets controller value to chosen option."""
        self.value = self.options.index(option)
    
    # call display selected on dropdown close somehow
        
    def display_selected(self):
        """Displays chosen option."""
        if self.value >= 0:
            try:
                self.main_button.text = self.options[self.value]
            except IndexError:
                self.main_button.text = 'Off'
        else:
            self.main_button.text = 'Off'
        
        if self.main_button.text == 'Off':
            self.main_button.state = 'normal'
        else:
            self.main_button.state = 'down'
        
        
class DualController(BaseController):
    """A controller made up of two different types of controllers.
       A list type controller (drop down, radio) and a numerical 
       type controller (slider, swipe).
    
       The numeric type controller remembers its value when it is
       de-activated with the list type controller."""
       
    def setup(self):
        """Makes a list of sub-controllers.
           Sets their sub-controller flag.
           Sets list and numeric controller.
           Carries out any sub-controller specific initialisations."""

        self.subcontrollers = [c for c in self.children \
                               if isinstance(c, BaseController)]
        
        for sub in self.subcontrollers:
            sub.is_subcontroller = True
            if type(sub) in [RadioController, DropDownController]:
                self.list_controller = sub
            elif isinstance(sub, SlideController) or \
                    isinstance(sub, TouchController):
                self.numeric_controller = sub
                self.saved_numeric_value = sub.value
            
            sub.offset = sub.midirange[0]
    
    def on_subcontroller_value(self, subcontroller):
        """Called when a sub-controller changes its value."""
        #print("osv", subcontroller)
        if subcontroller.value_in_midirange(subcontroller.value 
                                            + subcontroller.offset):
            if subcontroller is self.numeric_controller:
                self.set_main_value_from_numeric_value()
            elif subcontroller is self.list_controller:
                self.set_main_value_from_list_value()

    def on_dualcontroller_value(self):
        """Called when the dual-controller changes its value."""
        #print("odv")
        
        # only set num if num has changed (to 'save' num value)
        if self.numeric_controller.value_in_midirange(self.value):
            self.set_sub_value_from_main_value(self.numeric_controller)

        # always set list (no saving nessesary)            
        self.set_sub_value_from_main_value(self.list_controller)
        
    def display_selected(self):
        """Display the selected button/option on the list controller."""
        self.list_controller.display_selected()
    
    
    def on_all_other_values_option_selected(self):
        """Called when list button that represents numeric controller
           values is pressed."""
        self.numeric_controller.value = self.saved_numeric_value 
        self.set_main_value_from_numeric_value()
        self.display_selected()
        
    def set_main_value_from_numeric_value(self):
        """Sets value of dual-controller from numeric subcontroller
           value."""
        self.value = self.numeric_controller.value \
                        + self.numeric_controller.offset
        self.saved_numeric_value = self.numeric_controller.value
                        
    def set_main_value_from_list_value(self):
        """Sets value of dual-controller from list subcontroller
           value."""
        self.value = self.list_controller.value \
                        + self.list_controller.offset 
        self.display_selected()                 
    
    def set_sub_value_from_main_value(self, sub):
        """Sets value of subcontroller from dual-controller value."""
        sub.value = self.value - sub.offset


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
