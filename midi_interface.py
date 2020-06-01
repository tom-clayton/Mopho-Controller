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

class Midi():
    
    def __init__(self, synth, controllers):
        """Sets up midi interface"""
        alsaseq.client('Synth Control', 1, 1, False)
        
        # auto-connect:
        alsaseq.connectfrom(0, 28, 0)
        alsaseq.connectto(1, 28, 0)
        
        self.synth = synth
        self.controllers = controllers
        self.pause_midi_out = False

    
    # ----------------------------------------------------- #
    #                   MIDI OUT METHODS                    #
    # ----------------------------------------------------- #
    
    def send_cc(self, nrpn, value):
        """Sends out midi data for controller unless controller change
           was due to incoming midi."""

        # Midi out will be paused if message was due to incoming midi:
        if self.pause_midi_out:
            return

        # here we could check if controller has only changed by one to 
        # make use of more efficient midi messaging available in some 
        # synths.
        
        # Send out the midi message(s).
        # synth class will encode the midi messages, it will return a 
        # tuple of a 2 byte bytes objects for each message. One byte for
        # each cc data byte.

        for message in self.synth.encode_cc(nrpn, value):
            alsaseq.output((10, 1, 0, 253, (0, 0), (0, 0), (0,0), 
                            (0, 0, 0, 0, message[0], message[1]))) 
    
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
           """ 
        
        # Strip data from messages, combine and send to synth class:
        n_messages = self.synth.cc_message_chunks
        
        data = bytes([event[-1][-1]])
        while len(data) < n_messages:
            event = alsaseq.input()
            if event[0] == alsaseq.SND_SEQ_EVENT_CONTROLLER:
                data += bytes([event[-1][-1]])
        nrpn, value = self.synth.decode_cc(data)
        
        self.pause_midi_out = True
        self.controllers.set_controller_value(nrpn, value)
        self.pause_midi_out = False

    def receive_sysex(self, event):
        """Recieves system exclusive midi event.
        
           Recieves data in chunks.
           Strips sysex bytes.
           Sets values for all relevent controllers.
           """   

        # Check if message is a program dump:    
        if not self.synth.is_program_dump(event[-1][1:-1]):
            print("Unidentified sysex message.")
            return
        
        print("Incoming program dump")
       
        # Strip data from messages and combine:
        data = event[-1][1:]

        # total_chunks = self.synth.program_dump_message_chunks
        # n_chunks = 1
        
        # while n_chunks < total_chunks:
            # event = alsaseq.input()
            # if event[0] == alsaseq.SND_SEQ_EVENT_SYSEX:
                # data += event[-1] # does this need stripping too?
                # n_chunks += 1
        
        while data[-1] != 0xF7:
            event = alsaseq.input()
            if event[0] == alsaseq.SND_SEQ_EVENT_SYSEX:
                data += event[-1] 
        print(len(data), data[-2:])
        unpacked_data = self.synth.unpack_program_data(data[:-1])
        
        self.pause_midi_out = True
        self.controllers.set_all_values(unpacked_data)
        self.pause_midi_out = False

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
