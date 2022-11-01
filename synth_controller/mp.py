#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Mopho.py
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

class Synth():
    """Class of option data, parameter order and midi methods uniquie 
       to the DSI Mopho synth. Information taken from Mopho operators 
       manual."""
    
    # Any options for non numeric controllers, in a dict of tuples
    # with the tuples in order they are selected in the synth go here:
    options = {'glide': ('Fixed rate', 'Fixed rate auto', 'Fixed time', 
                     'Fixed time auto'),
           'key_assign': ('Low Note', 'Low Note, re-trigger', 'High Note',
                          'High Note, re-trigger', 'Last Note', 
                          'Last Note, re-trigger'),
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
                            'Sub Osc 2 Level'),
           'time_syncs': ('32 Step', '16 Step', '8 Step', '6 Step', '4 Step', 
                          '3 Step', '2 Step', '1.5 Step', '1 Step', 
                          '2/3 Steps', '1/2 Step', '1/3 Steps', '1/4 Step', 
                          '1/6 Step', '1/8 Step', '1/16 Step'),
           'lfo_shapes': ('Triangle', 'Rev. Saw.', 'Sawtooth', 'Square', 
                          'Random'),
           'sources': ('Off', 'Sequence Track 1', 'Sequence Track 2', 
                       'Sequence Track 3', 'Sequence Track 4', 'LFO 1', 
                       'LFO 2', 'LFO 3', 'LFO 4', 'Filter Envelope', 
                       'Amp Envelope', 'Envelope 3', 'Pitch Bend', 'Mod Wheel',
                       'Pressure', 'MIDI Breath', 'MIDI Foot', 
                       'MIDI Expression', 'Velocity', 'Note Number', 'Noise', 
                       'Audio In Envelope Follower', 'Audio In Peak Hold')}
    # It may be possible to store these in the kivy file and use a kivy
    # option property.
    
    # The total number of parameters in the synth goes here:
    number_of_parameters = 256
                       
    # If the paramters are not numberered in the order they come in a 
    # program dump, the order of nrpns must go here:
    # If all parameters come in nrpn order this tuple should be left out.                   
    # Only use None for unused parmeter slot, not for parameters that
    # aren't being controlled by the program.
    
    nrpn_order = tuple ([0, 1, 2, 3, 4, 114, 5, 6, 7, 8, 9, 115, 10, 11, 12, 
                    93, 96, 13, 14, 116, 15, 16, 17, 18, 19, 20, 21, 22, 
                    23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36, 29, 
                    37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 
                    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,60, 61, 62, 
                    63, 64, 98, 65, 66, 67, 68, 69, 70, 71, 72, 73,74, 
                    75, 76, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 111, 
                    112, 113, 91, 92, 97, 100, 94, 101, 77, 78, 79, 80,
                    105, 106, 107, 108] + \
                    [None for x in range(11)] + \
                    list(range(120, 200)) + \
                    [None for x in range(56)])
    
                
    # All parameters before a parameter being used must be included.
    # If they are not known just put in the position. This is to make
    # sure the remaining parameter's positions are correct.
    
    # If after a certain point, the nrpns of all remaining parameters 
    # are equal to the paramter's position in a program dump, the rest 
    # can be left out.
    
    # Note: This maybe changed to a (position, nrpn) tuple to save 
    # confusion.
    
    # The message to request a current program data dump from the synth 
    # via sysex messaging. As a bytes object, without sysex demimiters goes
    # here:
    current_program_dump_request = b'\x01\x25\x06'
    
    # The number of midi messages that a cc midi message comes from the
    # synth in goes here:
    cc_message_chunks = 4
    
    # Methods which will overide the base class with behaviour unique
    # to the synth (Can be left out to use default behaviour of base
    # class) go here:            
    def encode_cc(self, nrpn, value):
        """Encodes a tuple of midi messages to send from then nrpn 
           number and parameter value. Each message is in the form 
           of a 2 byte bytes object"""
        return (b'\x63' + bytes([nrpn>>7 & 0x7f]),
                b'\x62' + bytes([nrpn & 0x7f]),
                b'\x06' + bytes([value>>7 & 0x7f]),
                b'\x26' + bytes([value & 0x7f]))
        
    def decode_cc(self, midi_data):
        """Decodes nrpn number and parameter value from a bytes object
           """
        
        nrpn = midi_data[0] << 7 | midi_data[1]
        value = midi_data[2] << 7 | midi_data[3]
        
        return nrpn, value

    def is_program_dump(self, midi_data):
        """Asserts whether sysex data received from synth (with sysex
           delimiters stripped) is a program dump. Returns True or False.
           """
             
        if midi_data[2] == 0x02 or midi_data[2] == 0x03:
            return True
        else:
            return False
            
    def unpack_program_data(self, midi_data):
        """Unpacks midi program dump data into tuple of parameter values
           as ints. Packing format from page 44 of Manual"""
           
        # Strip header:
        if midi_data[2] == 0x02:
            # Saved program data dump. (the extra 2 bytes are bank and 
            # program)
            packed_data = midi_data[5:]
        elif midi_data[2] == 0x03:
            # Edit buffer data dump.
            packed_data = midi_data[3:]

        # Unpack:
        unpacked_data = []


        for i in range(0, len(packed_data), 8):
            chunk = packed_data[i: i+8]
            packing_byte = chunk[0]
            mask = 0x01
            for byte in chunk[1:]:
                if (packing_byte & mask):
                    unpacked_data.append(0x80 + byte)
                else:
                    unpacked_data.append(byte)
                mask = mask << 1
    
        return tuple(unpacked_data)

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
