import logging

from mpf.platforms.interfaces.light_platform_interface import LightPlatformSoftwareFade
from .can_command import MatrixLightCommand


class MatrixLight(LightPlatformSoftwareFade):
    def __init__(self, platform, number):
        self.log = logging.getLogger('Platform.DIYPinball.MatrixLight')
        self.platform = platform
        self.number = number
        self.board, self.light = [int(i) for i in self.number.split('-')]
        self.last_brightness = None

    def set_brightness(self, brightness: float):
        if self.last_brightness != brightness:
            cmd_brightness = int(255 * brightness)
            self.platform.send(MatrixLightCommand(self.board, self.light, cmd_brightness))
            self.last_brightness = brightness

    def off(self):
        if self.last_brightness != 0:
            self.platform.send(MatrixLightCommand(self.board, self.light, 0))
            self.last_brightness = 0
