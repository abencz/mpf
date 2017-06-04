import logging

from mpf.platforms.interfaces.light_platform_interface import LightPlatformInterface
from .can_command import MatrixLightCommand


class MatrixLight(LightPlatformInterface):
    def __init__(self, platform, number, subtype, platform_config):
        self.log = logging.getLogger('Platform.DIYPinball.MatrixLight')
        self.platform = platform
        self.config = platform_config
        self.number = number
        self.board, self.light = [int(i) for i in self.number.split('-')]
        self.last_brightness = None

    def set_brightness(self, brightness=255):
        if self.last_brightness != brightness:
            self.platform.send(MatrixLightCommand(self.board, self.light, brightness))
            self.last_brightness = brightness
