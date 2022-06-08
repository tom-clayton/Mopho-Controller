
import os
import json

SETUPS_DIR = 'setups'

class SetupManager(object):
    """Manage the different user setups available"""
    def __init__(self):
        self.setups_dir = os.path.join(os.getcwd(), SETUPS_DIR)
        self._load_main_settings()
        self._confirm_setup()
        self._load_setup_settings()

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

    def _save_setup_settings(self):
        """save the settings for the current setup"""
        with open(os.path.join(self.setup_dir, "settings.json"), "w") as fo:
            json.dump(self.setup_settings, fo, indent=4)

    @property
    def channels(self):
        return self.setup_settings['synth channels']

    @channels.setter
    def channels(self, value):
        """set synth channels and save settings"""
        # check for multiple values
        self.setup_settings['synth channels'] = value
        self._save_setup_settings()

    @property
    def initial_screen(self):
        return self.setup_settings['initial screen']

    @initial_screen.setter
    def initial_screen(self, value):
        """set synth channels and save settings"""
        self.setup_settings['initial screen'] = value
        self._save_setup_settings()

    @property
    def screens(self):
        """return a dict of kv files in current setup directory, with name
        without directory or extension as key and full filename as value."""
        output = {}
        for filename in [f for f in os.listdir(self.setup_dir) \
                          if f[-3:] == '.kv']:
            output[filename[:-3]] = os.path.join(self.setup_dir, filename)    
        return output
    
    @property
    def setups(self):
        """return all setups in setup directory"""
        return [f for f in os.listdir(self.setups_dir) \
                 if os.path.isdir(os.path.join(self.setups_dir, f))]

class NoSetupException(Exception):
    pass
