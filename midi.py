
from alsa_midi import SequencerClien, EventType, ControlChangeEvent,\
                      NonRegisteredParameterChangeEvent, SysExEvent

import threading

MSG_SYSEX_END   = 0xf7
MSG_PARAM_MSB    = 0x63
MSG_PARAM_LSB    = 0x62
MSG_VALUE_MSB     = 0x06
MSG_VALUE_LSB     = 0x26

class Midi(object):
    def __init__(self, cc_callback=None, sysex_callback=None):
        """Set up midi interface"""
        self._setup()

        self.cc_callback = cc_callback
        self.sysex_callback = sysex_callback

        self._create_data()
        
        input_thread = threading.Thread(
            target=self.poll, 
            daemon=True
        )
        input_thread.start()
    
    def _setup(self):
        """setup alsa midi"""
        self.client = SequencerClient("Synth Controller")
        self.port = self.client.create_port("main")

    def _create_data():
        """create empty received message data arrays"""
        self.nrpn_data = []
        self.sysex_data = []
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
        self.sysex_data[channel] = None
        
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
            self.data[event.channel]['param_msb'] = event.value
            self.check_nrpn(event.channel)
        elif event.param == MSG_PARAM_MSB:
            self.data[event.channel]['param_lsb'] = event.value
            self.check_nrpn(event.channel)
        elif event.param == MSG_VALUE_MSB:
            self.data[event.channel]['value_msb'] = event.value
            self.check_nrpn(event.channel)
        elif event.param == MSG_VALUE_MSB:
            self.data[event.channel]['value_lsb'] = event.value
            self.check_nrpn(event.channel)

        else: # standard cc
            self.cc_callback(event.channel, event.param, event.value) 
        
    def _check_nrpn(channel):
        """check if all parts of nrpn message have arrived"""
        if all(self.nrpn_data[channel]):
            param = self.nrpn_data[channel]['param_msb'] << 7 \
                    + self.nrpn_data[channel]['param_lsb']
            value = self.nrpn_data[channel]['value_msb'] << 7 \
                    + self.nrpn_data[channel]['value_lsb']

            self.cc_callback(self.channel, param, value)
            self._clear_channel_data(channel)       
        
    def _parse_sysex(self, event):
        """parse midi sysex message"""
        self.channel = event.channel
        if event.data[-1] != MSG_SYSEX_END:
            self.sysex_data == event.data
        else:
            self.sysex_data += event.data
            self.sysex_callback(self.channel, self.sysex_data)
            self._clear_channel_data(channel)

    def send_cc(self, channel, controller, value):
        """send standard control change midi message for given values"""
        self.client.event_ouput(
            ControlChangeEvent(channel, controller, value)
        )
        client.drain_output()
        
    def send_nrpn(self. channel, controller, value):
        """send a nrpn control change midi message for given values"""
        self.client.event_ouput(
            NonRegisteredParameterChangeEvent(channel, controller, value)
        )
        client.drain_output()
        
    def send_sysex(self, data):
        """send a system exclusive messsage with given data."""
        self.client.event_ouput(SysExEvent(data))
        client.drain_output()
        
