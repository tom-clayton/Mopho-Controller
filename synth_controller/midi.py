
from alsa_midi import SequencerClient, EventType, ControlChangeEvent,\
                      NonRegisteredParameterChangeEvent, SysExEvent

import threading

MSG_SYSEX_END   = 0xf7
MSG_PARAM_MSB    = 0x63
MSG_PARAM_LSB    = 0x62
MSG_VALUE_MSB     = 0x06
MSG_VALUE_LSB     = 0x26

class Midi(object):
    def __init__(self, connection=None):
        """Set up midi interface"""
        self._setup(connection)
        self._create_data_array()
        
        input_thread = threading.Thread(
            target=self._poll, 
            daemon=True
        )
        input_thread.start()

    def set_callbacks(self, cc_callback=None, sysex_callback=None,):
        """Set the midi in callbacks"""
        self.cc_callback = cc_callback
        self.sysex_callback = sysex_callback
    
    def _setup(self, connection):
        """setup alsa midi"""
        self.client = SequencerClient("Synth Controller")
        self.port = self.client.create_port("main")
        if connection:
            # connect to port
            pass

    def _create_data_array(self):
        """create empty received message data arrays"""
        self.sysex_data = b''
        self.nrpn_data = [i for i in range(16)]
        for i in range(16):
            self._clear_channel_data(i)      

    def _clear_channel_data(self, channel):
        """clear data for given channel"""
        self.nrpn_data[channel] = {
                "param_msb": None,
                "param_lsb": None,
                "value_msb": None,
                "value_lsb": None
            }   
        
    def _poll(self):
        """poll midi for input"""
        print ("thread started")
        while True:
            event = self.client.event_input()
            if event.type == EventType.CONTROLLER:
                self._parse_cc(event)
            elif event.type == EventType.SYSEX:
                self._parse_sysex(event)
     
    def _parse_cc(self, event):
        """parse a control change midi message"""
        if event.param == MSG_PARAM_MSB:
            self.nrpn_data[event.channel]['param_msb'] = event.value
            self._check_nrpn(event.channel)
        elif event.param == MSG_PARAM_LSB:
            self.nrpn_data[event.channel]['param_lsb'] = event.value
            self._check_nrpn(event.channel)
        elif event.param == MSG_VALUE_MSB:
            self.nrpn_data[event.channel]['value_msb'] = event.value
            self._check_nrpn(event.channel)
        elif event.param == MSG_VALUE_LSB:
            self.nrpn_data[event.channel]['value_lsb'] = event.value
            self._check_nrpn(event.channel)

        else: # standard cc
            if self.cc_callback:
                self.cc_callback(event.channel, event.param, event.value) 
        
    def _check_nrpn(self, channel):
        """check if all parts of nrpn message have arrived"""
        if all(map(
                lambda x: x is not None, 
                self.nrpn_data[channel].values()
            )):
            param = (self.nrpn_data[channel]['param_msb'] << 7) \
                    + self.nrpn_data[channel]['param_lsb']
                    
            value = (self.nrpn_data[channel]['value_msb'] << 7) \
                    + self.nrpn_data[channel]['value_lsb']
            
            if self.cc_callback:
                self.cc_callback(channel, param, value)
                
            self._clear_channel_data(channel)       
        
    def _parse_sysex(self, event):
        """parse midi sysex message"""
        if event.data[-1] != MSG_SYSEX_END:
            self.sysex_data = event.data
        else:
            self.sysex_data += event.data
            if self.sysex_callback:
                self.sysex_callback(self.sysex_data)
            self.sysex_data = b''

    def send_cc(self, channel, controller, value):
        """send standard control change midi message for given values"""
        self.client.event_output(
            ControlChangeEvent(channel, controller, value)
        )
        self.client.drain_output()
        
    def send_nrpn(self, channel, controller, value):
        """send a nrpn control change midi message for given values"""
        print(channel,controller, value)
        self.client.event_output(
            NonRegisteredParameterChangeEvent(channel, controller, value)
        )
        self.client.drain_output()
        
    def send_sysex(self, data):
        """send a system exclusive messsage with given data."""
        self.client.event_output(SysExEvent(data))
        self.client.drain_output()
        
