import logging

from mpf.platforms.interfaces.light_platform_interface import LightPlatformSoftwareFade
from .can_command import RGBLEDCommand


class RGBLED:
    def __init__(self, platform, number):
        self.log = logging.getLogger('Platform.DIYPinball.RGBLED')
        self.platform = platform
        self.number = number
        self.board, self.led = [int(i) for i in self.number.split('-')]
        self.color = [0, 0, 0]
        self.log.debug('Configured led {}'.format(self.number))
        self.clean = False

    def set_brightness(self, channel: int, brightness: float):
        brightness = int(255 * brightness)
        if brightness != self.color[channel]:
            self.color[channel] = brightness
            self.clean = False

    def update_state(self):
        if not self.clean:
            self.log.debug('Sending color {} to led {} on board {}'.format(self.color, self.led, self.board))
            self.platform.send(RGBLEDCommand(self.board, self.led, self.color))
            self.clean = True


class RGBLEDChannel(LightPlatformSoftwareFade):
    channel_map = {'r': 0, 'g': 1, 'b': 2}
    def __init__(self, led: RGBLED, channel) -> None:
        self.log = logging.getLogger('Platform.DIYPinball.RGBLEDChannel')
        self.led = led
        self.channel_char = channel
        self.channel = self.channel_map[channel]

    def set_brightness(self, brightness: float):
        self.led.set_brightness(self.channel, brightness)

    def off(self):
        self.led.set_brightness(self.channel, 0)

    @property
    def number(self):
        return '/'.join((self.led.number, self.channel_char))

    def get_board_name(self):
        return 'diypinball'
