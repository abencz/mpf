import logging

from mpf.platforms.interfaces.rgb_led_platform_interface import RGBLEDPlatformInterface
from .can_command import RGBLEDCommand


class RGBLED(RGBLEDPlatformInterface):
    def __init__(self, platform, config):
        self.log = logging.getLogger('Platform.DIYPinball.RGBLED')
        self.platform = platform
        self.config = config
        self.number = config['number']
        self.board, self.led = [int(i) for i in self.number.split('-')]

    def color(self, color):
        self.platform.send(MatrixLightCommand(self.board, self.led, color))
