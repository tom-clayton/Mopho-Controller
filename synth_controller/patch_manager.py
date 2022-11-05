
from synth_manager import IncorrectSynthError

import os

class PatchManager(object):
    """Loads, saves, sends and receives patches (full synth patches).

    param midi - midi interface object."""
    def __init__(
            self,
            midi,
            ui,
            controller_manager,
            synth_manager,
            error_handler
        ):
        """Store references to objects or relevent functions from objects"""
        self.send_sysex = midi.send_sysex
        self.ui = ui
        self.get_controller_values = controller_manager.get_controller_values
        self.set_controller_values = controller_manager.set_controller_values
        self.synth_manager = synth_manager
        self.error_handler = error_handler

        self.ui.bind(on_load_unconfirmed=self.on_load_unconfirmed)
        self.ui.bind(on_load_confirmed=self.on_load_confirmed)
        self.ui.bind(on_save_unconfirmed=self.on_save_unconfirmed)
        self.ui.bind(on_save_confirmed=self.on_save_confirmed)
        
    def _check_synth(self, synth):
        """Check if synth has patching details set in settings"""
        if self.synth_manager.is_patchable(synth):
            return true
        else:
            self.error_handler.error('NO_PATCH_DETAILS', synth)

    def on_load(self, synth):
        """Open a load dialogue in the ui"""
        if self._check_synth(synth):
            self.ui.load_dialogue(synth)

    def on_load_unconfirmed(self, synth, filename):
        """Confirm the load in the ui"""
        self.ui.confirm_popup(CONFIRM_LOAD, 'on_load_confirmed', (synth, filename))         

    def on_load_confirmed(self, data):
        """Load patch from hard disk"""
        synth, filename = data
        with open(filename, "rb") as fo:
            patch_data = fo.read()

        self._apply_patch(synth, patch_data)

    def _apply_patch(self, synth, data):
        """Parse, unpack and apply parameter values to controllers"""
        try:
            unpacked_data = self.synth_manager.unpack(synth, data[1:-1])
            self.set_controller_values(
                            self.synth_manager.get_channel(synth),
                            self.synth_manager.get_order(synth),
                            unpacked_data
                        )
        except IncorrectSynthError:
            self.error_handler.error('INCORRECT_SYNTH', synth)    
        

    def on_save(self, synth):
        """Open a load dialogue in the ui"""
        # check here for controllers (incl. dummies) for every parameter
        # or the patch will not be a complete patch, unless completed
        # from scratch
        if self._check_synth(synth):
            self.ui.save_dialogue(synth)
            
    def on_save_unconfirmed(self, synth, filename):
        """Confirm the save in the ui"""
        if os.path.exists(filename):
            self.ui.confirm_popup(CONFIRM_SAVE, 'on_save_confirmed', (synth, filename))
        pass


    def on_save_confirmed(self, synth, data):
        """Save patch to hard disk"""
        synth, filename = data
        patch_data = self.get_controller_values(
                                    synth,
                                    self.synth_manager.get_order(synth),
                                )

        packed_data = self.synth_manager.pack(synth, patch_data)
        
        with open(filename, "rb") as fo:
            fo.write(0xf0)
            fo.write(packed_data)
            fo.write(0xf7)


    def on_send(self, synth):
        """Get and pack controller values, create and send sysex message"""
        patch_data = self.get_controller_values(
                                    synth,
                                    self.synth_manager.get_order(synth),
                                )
        packed_data = self.synth_manager.pack(synth, patch_data)

        message = b'\xf0'
        message += self.synth_manager.get_header(synth)
        message += packed_data
        message += b'\xf7'
        self.send_sysex(message)

    def on_receive(self, synth):
        """Send request patch sysex message to synth"""
        if self.synth_manager.is_patchable(synth):
            message = self.synth_manager.get_request(synth)
            self.send_sysex(b'\xf0' + message + b'\xf7')
        else:
            self.error_handler.error('NO_PATCH_DETAILS', synth)

    def parse_sysex(self, message):
        """Find out which synth incoming sysex message is for.
        apply patch if possible"""
        synth = self.synth_manager.find_synth(message[1:-1])
        if synth:
            self._apply_patch(synth, message)
            
        
