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
    
    def __init__(self, synth):
        """Sets up midi interface"""
        alsaseq.client('Synth Control', 1, 1, False)
        
        # auto-connect:
        alsaseq.connectfrom(0, 28, 0)
        alsaseq.connectto(1, 28, 0)
        
        self.synth = synth
        self.midi_out_paused = False
        

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

        # Midi out will be paused if message was due to incoming midi:
        if self.midi_out_paused:
            self.midi_out_paused = False
            return
        
        # here we could check if controller has only changed by one to 
        # make use of more efficient midi messaging available in some 
        # synths.
        
        value = controller.get_value()
        
        # Send out the midi message(s).
        # synth class will encode the midi messages, it will return a 
        # tuple of a 2 byte bytes objects for each message. One byte for
        # each cc data byte.
        for message in self.synth.encode_cc(controller.nrpn, value):
            alsaseq.output((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                            (0, 0, 0, 0, message[0], message[1]))) 
        
        if DEBUG_OUTPUT:
            print("sent", controller)

    def send_program(self):
        """Sends value for every main controller."""
        for controller in self.controllers:
            self.send_cc(controller)
    
    def request_current_program(self): 
        """Sends request for the current program data"""
        
        request = b'\xF0' + self.synth.current_program_dump_request \
                    + b'\xF7'           
        alsaseq.output((130, 0, 0, 253, (0, 0), (0, 0), (0,0), 
                        (request,)))
        
    # ----------------------------------------------------- #
    #                   MIDI IN METHODS                     #
    # ----------------------------------------------------- #
    

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
        
        # Strip data from messages, combine and send to synth class:
        n_messages = self.synth.cc_message_chunks
        
        data = bytes([event[-1][-1]])
        while len(data) < n_messages:
            event = alsaseq.input()
            if event[0] == alsaseq.SND_SEQ_EVENT_CONTROLLER:
                data += bytes([event[-1][-1]])
        nrpn, value = self.synth.decode_cc(data)
        
        try:
            # Look up controller:
            controller = self.controller_from_nrpn(nrpn)
        
            # Pause midi out, so received message isn't sent back out 
            # when controller value is updated:
            self.midi_out_paused = True
            controller.set_value(value)
        
            if DEBUG_OUTPUT:
                print("received", controller)
                
        except IndexError:
            pass


    def receive_sysex(self, event):
        """Recieves system exclusive midi event.
        
           Recieves data in two chunks.
           Strips packing bytes.
           Sets values for all relevent controllers.
           """   

        # Check if message is a program dump:    
        if not self.synth.is_program_dump(event[-1][1:-1]):
            print("Unidentified sysex message.")
            return
        
       
        # Strip data from messages and combine:
        data = event[-1][1:-1]
        
        total_chunks = self.synth.program_dump_message_chunks
        n_chunks = 1
        
        while n_chunks < total_chunks:
            event = alsaseq.input()
            if event[0] == alsaseq.SND_SEQ_EVENT_SYSEX:
                data += event[-1]
                n_chunks += 1
        
        # Unpack program into list of integers:
        unpacked_data = self.synth.unpack_program_data(data)
        
        # Set controllers in correct order:
        for index, nrpn in enumerate(self.synth.nrpn_numbers):
            value = unpacked_data[index]
            try:
                controller = self.controller_from_nrpn(nrpn)
            except IndexError:
                pass
                
            self.midi_out_paused = True
            controller.set_value(value) 
 
    def controller_from_nrpn(self, nrpn):
        controllers_found =  [c for c in self.controllers \
                                    if c.nrpn == nrpn]
                                
        if len(controllers_found) == 0:
            print ("No controller found for nrpn ", nrpn)
        elif len(controllers_found) > 1:
            print ("Warning: Multiple top level controllers found for nrpn",
                    nrpn)
            print ("Using: ", controllers_found[0])
            for controller in controllers_found[1:]:
                print("Ignoring: ", controller)
        
        return controllers_found[0]  

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
