#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  controller_manager.py
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

import controllers
from controllers import BaseController

class ControllerManager():
    def setup_controllers(self, midi, synth):
        """Creates list of main controllers.
           Calls setup for controllers that need it.
           Passes midi object to all main controllers."""
        self.synth = synth
        self.midi = midi
        
        all_controllers = controllers.all_controllers
        
        for controller in all_controllers:
            controller.synth = synth   
            controller.setup()
            
        self.controllers = [c for c in all_controllers if not \
                                c.is_subcontroller]    
        self.sub_controllers = [c for c in all_controllers if \
                                c.is_subcontroller]
       
        for controller in all_controllers:
            controller.display_selected()
                
        # create ordered list including blank controllers for parameter
        # we are not controlling but still want to loaded, saved and 
        # sent to the synth:
        
        self.ordered_controllers = []
        
        if hasattr(self.synth, 'nrpn_order'):
            self.nrpn_order = self.synth.nrpn_order
        else:
            self.nrpn_order = range(self.synth.number_of_parameters)
            
        for i, nrpn in enumerate(self.nrpn_order):
            if nrpn is not None:
                try:
                    self.ordered_controllers.append(
                                self.controller_from_nrpn(nrpn))
                except IndexError:
                    blank = BaseController()
                    blank.nrpn = nrpn
                    self.ordered_controllers.append(blank)
            else:
                self.ordered_controllers.append(None)
            
        print(self.synth.number_of_parameters, 
              len(self.nrpn_order), 
              len(self.ordered_controllers))
            
        for controller in [c for c in self.ordered_controllers if c is 
                                                        not None]:
            controller.midi = midi
        
    def set_controller_value(self, nrpn, value):
        """Sets relevant controllers value"""
        try:
            controller = self.controller_from_nrpn(nrpn)
            controller.set_value(value)
        except IndexError:
            # print(f"No controller for {nrpn}")
            pass
            
    def set_all_values(self, values):
        """Sets all controllers values from tuple of values in order
           they come from a program dump."""
        for i, value in enumerate(values):
            controller = self.ordered_controllers[i]
            if controller is not None:
                controller.set_value(value)
        
    def send_program(self):
        """Sends value for every main controller."""
        for controller in self.ordered_controllers:
            if controller is not None:
                controller.send_cc()
          
    def get_save_data(self):
        """Returns a bytearray of all synth parameter values, including 
           ones not controlled by a controller."""
        output = []   
        for i, controller in enumerate(self.ordered_controllers):
            if controller is not None:
                output.append(controller.get_value())
            else:
                output.append(0)

        return bytearray(output)
    
    def set_load_data(self, binary_data):
        """Receives load data from file manager."""
        data = [x for x in binary_data]
        self.midi.pause_midi_out = True
        self.set_all_values(data)
        self.midi.pause_midi_out = False
        self.send_program()
                
    def controller_from_nrpn(self, nrpn):
        """Returns controller with given nrpn number.
           Will raise IndexError if there isn't one."""
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
            
    def print_ordered_controllers(self):
        """Prints the value of every controller (including blanks) 
           to stdout."""
        for controller in self.ordered_controllers:
            print (controller)

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
