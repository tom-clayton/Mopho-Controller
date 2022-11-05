
import os
import json

SETUPS_DIR = 'setups'

class SetupManager(object):
    """Manage the different user setups and their settings"""
    def __init__(self, ui):
        self.ui = ui
        self.setups_dir = os.path.join(os.getcwd(), SETUPS_DIR)
        self._load_main_settings()
        self._confirm_setup()
        self._load_setup_settings()

        self.ui.bind(on_channel_selection=self.on_channel_selection)

    def _load_main_settings(self): 
        """load settings from current directory"""
        self.initial_setup = None
        try:
            with open ("settings.json") as fo:
                settings = json.load(fo)
                self.initial_setup = settings['initial setup']
        except FileNotFoundError:
            pass

    def _confirm_setup(self):
        """check if intial setup found, use first setup found if not,
        raise error if no setups found."""
        setups = self.setups
        if self.initial_setup in setups:
            self.setup_dir = os.path.join(self.setups_dir, self.initial_setup)
        elif setups:
            self.setup_dir = os.path.join(self.setups_dir, self.setups[0])
        else:
            raise NoSetupException

    def _load_setup_settings(self):
        """load the settings for the current setup"""
        try:
            with open(os.path.join(self.setup_dir, "settings.json")) as fo:
                self.setup_settings = json.load(fo)
        except FileNotFoundError:
            self.setup_settings = {
                                'initial screen': None,
                                'synth channels': {},
                            }

    def _load_screens(self):
        """Create a dict of kv files in current setup directory, with name
        without directory or extension as key and full filename as value."""
               

    def _save_setup_settings(self):
        """save the settings for the current setup"""
        with open(os.path.join(self.setup_dir, "settings.json"), "w") as fo:
            json.dump(self.setup_settings, fo, indent=4)


    def build_screens(self):
        """Build the screens found in the setup into the ui.
        Set the initial screen"""
        kv_files = {}
        for filename in [f for f in os.listdir(self.setup_dir) \
                          if f[-3:] == '.kv']:
            kv_files[filename[:-3]] = os.path.join(self.setup_dir, filename)
        self._load_screens()
        self.ui.build_screens(kv_files)
        self.ui.set_screen(self.initial_screen)

    def assign_channels(self, synths):
        """Check if all controlled synths have a midi channel assigned in
        settings.
        Run midi channel selction if not."""
        synth_missing = False
        channels = {}
        for synth in synths:
            if synth not in self.setup_settings['synth channels']:
                channels[synth] = None
                synth_missing = True
            else:
                channels[synth] = self.setup_settings['synth channels'][synth]

        if synth_missing:
            self.ui.channel_selection_popup(channels)
        else:
            self.setup_settings['synth channels'] = channels

    def on_channel_selection(self, _, channels): 
        """Set the channels dict as requested in the channel selection popup.
        Assign channels in controllers"""
        self.setup_settings['synth channels'] = channels
        self._save_setup_settings()

    @property
    def channels(self):
        return self.setup_settings['synth channels']

    @property
    def initial_screen(self):
        return self.setup_settings['initial screen']

    @initial_screen.setter
    def initial_screen(self, value):
        """set synth channels and save settings"""
        self.setup_settings['initial screen'] = value
        self._save_setup_settings()
    
    @property
    def setups(self):
        """return all setups in setup directory"""
        return [f for f in os.listdir(self.setups_dir) \
                 if os.path.isdir(os.path.join(self.setups_dir, f))]

class NoSetupException(Exception):
    pass
