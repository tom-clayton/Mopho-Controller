#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  synth.py
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

# Maybe change to a template and not inherit.

class Synth():
	"""A parent class for all the different synth sub classes to inherit
	   from. See Mopho.py as an example of how to create a sub class"""
	
	# options = {}
                          
	# nrpn_numbers = ()
	
	# program_dump_request = b'' 
	
	# program_dump_message_chunks = 0
	
	# default methods, can be overwitten in sub classes
	def encode_cc(self, nrpn, value):
		pass
	
	def decode_cc(self, midi_data):
		pass
		
	def decode_program_dump(self, midi_data):
		pass
		
	def decode_program_dump(self, midi_data):
		pass
		
	
def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
3
