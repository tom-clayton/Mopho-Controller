
from synth_manager import IncorrectSynthError

class PatchManager(Object):
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
        """Store references to objects"""
        self.midi = midi
        self.ui = ui
        self.controller_manager = controller_manager
        self.synth_manager = synth_manager
        self.error_handler = error_handler

        self.ui.bind(on_load_confirmed=self.on_load_confirmed)

        
    def _check_synth(self, synth):
        """Check if synth has patching details set in settings"""
        if self.synth_manager.is_patchable(synth):
            return true
        else:
            self.error_handler.error_message('NO_PATCH_DETAILS', synth)

    def on_load_unconfirmed(self, data):
        """open a confirm popup to confirm patch load"""
        if self._check_synth(data[0]):
            self.ui.confirm_popup(CONFIRM_LOAD, 'on_load_confirmed', data)         

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
        except IncorrectSynthError:
            self.error_handler.error_message('INCORRECT_SYNTH', synth)
            
        self.controller_manager.set_controller_values(
                                        synth,
                                        self.synth_manager.get_order(synth),
                                        unpacked_data
                                    )

    def save_patch(self, synth, filename):
        pass

    def parse_sysex(self, message):
        pass
        
