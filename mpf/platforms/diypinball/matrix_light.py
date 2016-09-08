import logging

from mpf.platforms.interfaces.matrix_light_platform_interface import MatrixLightPlatformInterface
from .can_command import MatrixLightCommand


class MatrixLight(MatrixLightPlatformInterface):
    def __init__(self, platform, config):
        self.log = logging.getLogger('Platform.DIYPinball.MatrixLight')
        self.platform = platform
        self.config = config
        self.number = config['number']
        self.board, self.light = [int(i) for i in self.number.split('-')]
        self.last_brightness = None

    def on(self, brightness=255):
        if self.last_brightness != brightness:
            self.platform.send(MatrixLightCommand(self.board, self.light, brightness))
            self.last_brightness = brightness

    def off(self):
        if self.last_brightness != 0:
            self.platform.send(MatrixLightCommand(self.board, self.light, 0))
            self.last_brightness = 0
