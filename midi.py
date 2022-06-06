
import rtmidi_python as rtmidi

MSG_CC          = 0xb0
MSG_SYSEX_START = 0xf0
MSG_SYSEX_END   = 0xf7
MSG_NRPN_MSB    = 0x63
MSG_NRPN_MSB    = 0x62
MSG_VAL_MSB     = 0x06
MSG_VAL_MSB     = 0x26


class Midi(object):
    def __init__(self, port=0, cc_callback, sysex_callback):
        """Set up midi interface"""
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_port(port)

        self.midi_in = rtmidi.MidiIn()
        self.midi_in.callback = self._on_midi
        self.midi_in.open_port(port)

        self.cc_callback = cc_callback
        self.sysex_callback = sysex_callback
        
    def send_cc(self, channel, controller, value):
        """send a control change midi midi_data for given values"""
        midi_out.send_message([MSG_CC | (channel-1), controller, value])

    def send_nrpn(self, channel, nrpn, value):
        """send a control change midi messsage for given values"""
        midi_out.send_message([
                MSG_CC | (channel -1),
                MSG_NRPN_MSB, nrpn >> 7,
                MSG_NRPN_LSB, nrpn & 0x7f,
                MSG_VAL_MSB, value >> 7,
                MSG_VAL_LSB, value & 0x7f
            ])

    def send_sysex(self, message):
        """send a system exclusive messsage."""
        msg = [MSG_SYSEX_START]
        msg.extend(message)
        msg.extend(MSG_SYSEX_END)
        midi_out.send_message(msg)

    def _on_midi(message, time_stamp):
        """parse status byte and deal with midi messsage"""
        print (message, time_stamp)

        # parse status byte:
        message_type = message[0] & 0xf0

        if message_type == MSG_CC:  
            self._receive_cc(message)
        elif message_type == MSG_SYSEX:
            self._receive_sysex(message)

    def _receive_cc(data):
        """receive a control change message"""
        if data[1] not in [
                        MSG_NRPN_MSB,
                        MSG_NRPN_LSB,
                        MSG_VAL_MSB,
                        MSG_VAL_LSB,
                    ]:
            # Standard CC control change:
            #self.cc_callback(data[0] & 0x0f, data[1], data[2])
            print(data, " control change ", data[0] & 0x0f, data[1], data[2])
        else:
            #self.cc_callback(
            #                data[0] & 0x0f,
            #                data[1] << 7 | data[2],
            #                data[3] << 7 | data[4]
            #            )
            print(
                data,
                " nrpn change ",
                data[0] & 0x0f,
                data[1] << 7 | data[2],
                data[3] << 7 | data[4]
            )
               
    def _receive_sysex(midi_data):
        """receive a system exclusive message"""
        print (midi_data)

        

        

