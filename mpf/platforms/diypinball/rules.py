from mpf.platforms.interfaces.driver_platform_interface import PulseSettings

class PulseOnHitRule(object):
    def __init__(self, coil):
        self.coil = coil

    def process_event(self, event):
        if event.data[0] == 1:
            self.coil.pulse(PulseSettings(1.0, 10))


class PulseOnHitAndReleaseRule(object):
    def __init__(self, coil):
        self.coil = coil

    def process_event(self, event):
        if event.data[0] == 1:
            self.coil.pulse(PulseSettings(1.0, 10))


class PulseOnHitAndEnableAndReleaseRule(object):
    def __init__(self, coil):
        self.coil = coil
        self.state = 0

    def process_event(self, event):
        if event.data[0] == 1:
            self.coil.enable(None)
        else:
            self.coil.disable(None)
