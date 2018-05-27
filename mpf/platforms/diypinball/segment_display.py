import logging

from mpf.platforms.interfaces.segment_display_platform_interface import SegmentDisplaySoftwareFlashPlatformInterface
from .can_command import TextSetCommand


class SegmentDisplay(SegmentDisplaySoftwareFlashPlatformInterface):
    def __init__(self, platform, number):
        super().__init__(number)

        self.log = logging.getLogger('Platform.DIYPinball.SegmentDisplay')
        self.platform = platform
        self.board = int(number)

    def _set_text(self, text: str) -> None:
        self.log.warn('Setting display {} to "{}"'.format(self.board, text))
        self.platform.send(TextSetCommand(self.board, text))

    def get_board_name(self):
        return 'diypinball'
