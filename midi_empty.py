
class Midi(object):
    """Allow testing without sending midi"""
    def __init__(self, a, b):
        pass
    def send_nrpn(self, channel, nrpn, value):
        print(f"channel:{channel} nrpn:{nrpn} value:{value}")
        

