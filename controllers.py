#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  controllers.py
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
                            ObjectProperty, BoundedNumericProperty,\
                            ListProperty, AliasProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.lang import Builder

Builder.load_file('controllers.kv')

class BaseController(BoxLayout):
    """Controller base class
       
       A controller controls a parameter of the synth.
       BaseController must be inherited by a controller sub-class.
       Setup must be called once for every controller.
       value is parameter value, midi value has offset added.
       Bind to controller event 'on_send' to receive out-going midi-values
       when controller value changes.
       Set controller with midi value via 'set_without_sending_midi'
       to avoid repeating midi.
       Controller objects are created in the kv file.
       """ 
    
    # Default controller properties. Set by kv file if required:
    name = StringProperty('')       
    synth = StringProperty(None)    
    channel = NumericProperty(0)
    nrpn = NumericProperty(None)
    value = BoundedNumericProperty(0, min=0, max=127)
    minimum = NumericProperty(0)
    maximum = NumericProperty(127)
    offset = NumericProperty(0)
    linked = ListProperty([])
    notes = BooleanProperty(False)

    def get_midi_value(self):
        """get controller value with midi offset included"""
        return self.value + self.offset
    
    def set_midi_value(self, value):
        """set controller value if within correct range
        will trigger on_midi_value callback"""
        if self.midi_value == value:
            self.locked = False
            return
        try:
            self.value = value - self.offset
            self.saved_value = self.value
        except ValueError:
            self.locked = False   
        
    midi_value = AliasProperty(get_midi_value, set_midi_value, bind=['value'])

    def __init__(self, **kwargs):
        self.register_event_type('on_send')
        super(BaseController, self).__init__(**kwargs)
        self.locked = False
        self.link_locked = False
        self.callback = None

    def setup(self, *kwargs):
        """Called once at startup,
        set limits for value bounded property,    
        call setup for subclasses."""
        self.property('value').set_min(self, self.minimum)
        self.property('value').set_max(self, self.maximum)
        if self.value < self.minimum:
            self.set_without_sending_midi(self.minimum + self.offset)
        self.sub_setup()

    def sub_setup(self, *kwargs):
        """overridden by subclass"""
        pass
        
    def display_selected(self):
        """Called when contoller selection should be displayed to
           screen.
           overridden by subcalss"""
        pass
    
    def set_without_sending_midi(self, value):
        """change controller value without sending out a midi message
        input should be raw midi value"""
        self.locked = True
        self.midi_value = value
        self.display_selected()

    def on_midi_value(self, instance, value):
        """Respond to a change in controller value.
           Display chosen value if approriate for controller.
           Send out value over midi if change was due to ui.
           """  
        self.display_selected()

        if self.locked:
            self.locked = False
        else:
            for linked in self.linked:
                linked.set_without_sending_midi(self.midi_value)
            self.dispatch('on_send', self.channel, self.nrpn, self.midi_value)

    def on_send(self, *args):
        pass
        #print(self)

    def add_callback(self, callback):
        """add acallback for notifying value changes"""
        self.callback = callback
            
    def note(self):
        """Returns value as musical note."""
        notes = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 
                 'A#', 'B')
        return notes[self.value%12] + str(self.value//12)
    
    def __repr__(self):
        return f"<{self.synth}>{type(self)}<{self.nrpn}>:{self.name} {self.value}"

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
    button = ObjectProperty()
    def display_selected(self):
        """display button state"""
        self.button.state = 'down' if self.value == 1 else 'normal' 

class RadioController(BaseController):
    """A radio switch type conntroller.
    
       The controller made up of multiple radio buttons, where each 
       one represents a value or values of the controller."""
    group = StringProperty(None)
    def add_buttons(self, buttons):
        """keep reference to buttons."""
        pass
    def sub_setup(self):
        self.buttons = ToggleButtonBehavior.get_widgets(self.group)
        for button in self.buttons:
            button.set_controller(self)

    def display_selected(self):
        """Displays which button is selected for controller."""
        for button in self.buttons:
            button.state = 'normal'
            if button.value >= 0:
                if self.midi_value == button.value:
                    button.state = 'down'
            elif button.minimum <= self.midi_value <= button.maximum:
                button.state = 'down'


            

class SwipeController(BaseController): 
    """A swipe type controller.
    
       The value is changed by a touch/click then draging up or down, or 
       mouse scrolling over controller"""
    text_label = ObjectProperty()

    def _on_down(self, wid, touch):
        """Grabs touch event if click/touch is over controller."""
        if touch.x >= self.x and touch.x <= self.x + self.size[0] and\
           touch.y >= self.y and touch.y <= self.y + self.size[1]:
            # touch belongs to this controller, proceed
            touch.grab(self)
            if touch.is_mouse_scrolling:
                try:
                    if touch.button == 'scrolldown': 
                        self.value += 1
                    elif touch.button == 'scrollup':
                        self.value -= 1
                except ValueError:
                    pass        
        
    def _on_move(self, wid, touch):
        """Changes controllers value coresponding to move after click/touch."""
        if touch.grab_current is self:
            try:   
                self.value = int(self.value + touch.dy)
            except ValueError:
                pass
            
    def _on_up(self, wid, touch):
        """Releases 'grab' of touch event on click/touch up."""
        if touch.grab_current is self:
            touch.ungrab(self)

    def display_selected(self):
        """displays controllers value"""
        self.text_label.text = str(self.value)

class DropDownController(BaseController):
    """A drop down type controller.
    
       The value is selected from a drop down list. """
    option_list = StringProperty('')
    options = ListProperty([])
    
    def sub_setup(self):
        """Creates the drop down list for the controller."""
        self.dropdown = DropDown()
        self.extra_options = []
        self._add_options_from_kivy()
        self.main_button = [widget for widget in self.children 
                       if isinstance(widget, Button)][0]

        for option in self.options:
            btn = Button(text=option, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
            
        self.main_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self._select_option)
        self.dropdown.bind(on_dismiss=self._on_dismiss)

    def _on_dismiss(self, button):
        """display selected option if dropdwon is dismissed"""
        self.display_selected()

    def _select_option(self, i, option):
        """Sets controller value to chosen option."""
        if option not in [o.name for o in self.extra_options]:
            self.value = self.options.index(option)
        else:
            for extra_option in self.extra_options:
                if option == extra_option.name:
                    try:
                        self.value = extra_option.value
                    except AttributeError:
                        try:
                            self.value = self.saved_value
                        except AttributeError:
                            self.value = extra_option.minimum
                        

    def add_options(self, options):
        """sets list of options on the dropdown"""
        self.options = options

    def _add_options_from_kivy(self):
        """adds any extra options from kivy file"""
        for child in self.children:
            if type(child) == Option:
                self.extra_options.append(child)
                self.options.append(child.name)
        
    def display_selected(self):
        """Displays chosen option."""
        self.main_button.text = 'Off'
        self.main_button.state = 'normal'

        for option in self.extra_options:
            if option.minimum <= self.value <= option.maximum:
                self.main_button.text = option.name
                self.main_button.state = 'down'
                return
        try:
            self.main_button.text = self.options[self.value]
            self.main_button.state = 'down'
        except IndexError:
            pass

class RadioButton(ToggleButton):
    """A radio button.
    
       Only one radio button in a controller can be selected at any
       time."""
    group = StringProperty(None)
    value = NumericProperty(-1)
    minimum = NumericProperty(0)
    maximum = NumericProperty(127)
        
    def set_controller(self, controller):
        """keep reference to controller"""
        self.controller = controller

    def on_press(self):
        """Radio button pressed.
        
           Sets value of radiocontroller"""
        if self.value >= 0:
            self.controller.value = self.value
        else:
            try:
                self.controller.value = self.controller.saved_value
            except AttributeError:
                self.controller.value = self.minimum
        self.controller.display_selected()

class Option(Widget):
    """An option in a drop down menu."""
    pass


class TestController(BaseController):
    """for testing purposes"""
    pass
        


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
