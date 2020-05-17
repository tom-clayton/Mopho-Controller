#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  midi_interface.py
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

import alsaseq

# alsaseq midi message tuple definition:
# (type, flags, tag, queue, time stamp, source, destination, data)

DEBUG_OUTPUT = True

class Midi():
    
    def __init__(self):
        """Sets up midi interface"""
        alsaseq.client('Mopho control', 1, 1, False)
        
        # auto-connect:
        alsaseq.connectfrom(0, 28, 0)
        alsaseq.connectto(1, 28, 0)
        
        self.last_controller_recieved = None
        

    def register_controllers(self, controllers):
        """Registers list of top level controllers, in order they come
           from synth in a program data dump"""
        self.controllers = controllers

    # ----------------------------------------------------- #
    #                   MIDI OUT METHODS                    #
    # ----------------------------------------------------- #
    
    def send_cc(self, controller):
        """Sends out midi data for controller unless controller change
           was due to incoming midi."""

        # Check if midi was due to incoming midi:
        if controller == self.last_controller_recieved:
            self.last_controller_recieved = None
            return
        
        # here we will check if controller has only changed by one to 
        # make use of more efficient midi messaging available in some 
        # synths.
        
        value = controller.value + controller.offset
        
        # 4 messages per cc, unique to mopho
        alsaseq.output((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                            (0, 0, 0, 0, 0x63, 
                            controller.nrpn_number >> 7 & 0x7F)))
                            
        alsaseq.output((10, 1, 0, 253, (0, 0), (0, 0), (0,0),
                            (0, 0, 0, 0, 0x62, 
                            controller.nrpn_number & 0x7F)))
                            
        alsaseq.output((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                            (0, 0, 0, 0, 0x06, 
                            value >> 7 & 0x7F)))
                            
        alsaseq.output((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                            (0, 0, 0, 0, 0x26, 
                            value & 0x7F)))
        if DEBUG_OUTPUT:
            print("sent", controller)

    def send_program(self):
        """Sends value for every main controller."""
        for controller in self.controllers:
            self.send_cc(controller)
    
    def request_current_program(self): 
        """Sends request edit buffer sys ex message"""
        
        # make a send sysex function
        
        # unique to mopho:
        print ("sending sysex")
        alsaseq.output((130, 0, 0, 253, (0, 0), (0, 0), (0,0), 
                        (b'\xF0\x01\x25\x06\xF7',)))
        
    # ----------------------------------------------------- #
    #                   MIDI IN METHODS                     #
    # ------------------------print("lcr", self.last_controller_recieved)----------------------------- #
    

    def check_midi(self, dt):
        """Recieves incoming midi"""
        if alsaseq.inputpending():
            event = alsaseq.input()
            if event[0] == alsaseq.SND_SEQ_EVENT_CONTROLLER:
                self.receive_cc(event)
            elif event[0] == alsaseq.SND_SEQ_EVENT_SYSEX:
                self.receive_sysex(event)


    def receive_cc(self, event):
        """Recieves control change midi event.
        
           Sets relevent contoller value.
           Sets last_controller_recevied so received message is not
           sent back out.
           """ 

        # uinque to mopho (comes in four messages)
        cc_data = [event[-1][-1]]
        while len(cc_data) < 4:
            event = alsaseq.input()
            cc_data.append(event[-1][-1])
        nrpn = cc_data[0] << 7 | cc_data[1]
        value = cc_data[2] << 7 | cc_data[3]
        
        controller = [c for c in self.controllers \
                        if c.nrpn_number == nrpn][0]
         
        self.last_controller_recieved = controller
        controller.value = value - controller.offset
        
        if DEBUG_OUTPUT:
            print("received", controller)

    def receive_sysex(self, event):
        """Recieves system exclusive midi event.
        
           Recieves data in two chunks.
           Strips packing bytes.
           Sets values for all relevent controllers.
           """
        # unique to mopho: needs fixing
        print (event[-1][-1])
        return
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
                controllers[param].recieved_midi(value)
            except IndexError:
                pass
                
   
    

        
def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
