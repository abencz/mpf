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
        self.last_color = None
        self.log.debug('Configured led {}'.format(self.number))

    def color(self, color):
        if color != self.last_color:
            self.log.debug('Sending color {} to led {} on board {}'.format(color, self.led, self.board))
            self.platform.send(RGBLEDCommand(self.board, self.led, color))
            self.last_color = color
