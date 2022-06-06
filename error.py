
error_message = {
    'NO_SYNTH_DATA': lambda synth: f"No data for '{synth}' type synth.",
    'NO_SYNTHS': lambda channel: "No synths registered in settings file"\
                                + f"using default midi channel: {channel}.",
    'SYNTH_NOT_REGISTERED': lambda synth: f"synth {synth} found in kv file,"\
                                + "but not registered in kv file.",
}

class ErrorHandler(object):

    def error(self, name, data):
        """print error message to screen. change to log ???"""        
        print(error_message[name](data))
