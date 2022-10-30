

class PatchManager(Object):
    """Loads, saves, sends and receives patches (full synth patches).

    param midi - midi interface object."""
    def __init__(self, midi, ui, controller_manager, synth_data, error_callback):
        """Store references to objects"""
        self.midi = midi
        self.ui = ui
        self.controller_manager = controller_manager
        self.synth_data = synth_data
        self.error_callback = error_callback

        self.ui.bind(on_load_confirmed=self.on_load_confirmed)

        
    def _check_synth(self, synth):
        """Check if synth has patching details set in settings"""
        if self.synth_data[synth].nrpn_order:
            return true
        else:
            self.error_callback()

    def on_load_unconfirmed(self, data):
        """open a confirm popup to confirm patch load"""
        if self.check_synth(data[0]):
            self.ui.confirm_popup(CONFIRM_LOAD, 'on_load_confirmed', data)         

    def on_load_confirmed(self, data):
        """Load patch from hard disk"""
        synth, filename = data
        with open(filename, "rb") as fo:
            patch_data = fo.read()

        self.apply_patch(synth, patch_data)

    def apply_patch(synth, data):
        """Parse, unpack and apply parameter values to controllers"""
        # unpack values from data

        self.controller_manager.set_controller_values(
                                    synth,
                                    self.synth_data[synth].nrpn_order,
                                    unpacked_data
                                )

    def save_patch(self, synth, filename):
        pass

    def parse_sysex(self, message):
        pass
        
