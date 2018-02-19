import struct

from .feature import Feature


class CANCommand(object):
    def __init__(self, board, device):
        self.prio = 0
        self.board_specific = True
        self.board = board
        self.feature_type = Feature.system
        self.feature_number = device
        self.msg_type = 0
        self.data = b''
        self.request = False

    @property
    def cob_id(self):
        cob_id = 0
        cob_id |= (self.prio & 0x0f) << 25
        bs = 1 if self.board_specific else 0
        cob_id |= bs << 24
        cob_id |= (self.board & 0xff) << 16
        cob_id |= (self.feature_type.value & 0x0f) << 12
        cob_id |= (self.feature_number & 0x0f) << 8
        cob_id |= (self.msg_type & 0x0f) << 4
        return cob_id

    def __str__(self):
        return 'P: {}, BS: {}, B: {}, FT: {}, FN: {}, MT: {}, D: {}'.format(self.prio,
                                                                            self.board_specific,
                                                                            self.board,
                                                                            self.feature_type,
                                                                            self.feature_number,
                                                                            self.msg_type,
                                                                            repr(self.data))


class DriverStateCommand(CANCommand):
    def __init__(self, board, driver, state):
        super(DriverStateCommand, self).__init__(board, driver)
        self.feature_type = Feature.driver
        state = 1 if state else 0
        self.data = struct.pack('B', state)


class DriverPulseCommand(CANCommand):
    def __init__(self, board, driver, milliseconds):
        super(DriverPulseCommand, self).__init__(board, driver)
        self.feature_type = Feature.driver
        self.data = struct.pack('BB', 1, milliseconds)


class MatrixLightCommand(CANCommand):
    def __init__(self, board, light, brightness):
        super(MatrixLightCommand, self).__init__(board, light)
        self.feature_type = Feature.lamp
        self.data = struct.pack('B', brightness)


class RGBLEDCommand(CANCommand):
    def __init__(self, board, led, color):
        super(RGBLEDCommand, self).__init__(board, led)
        self.feature_type = Feature.rgb_led
        self.data = struct.pack('BBB', *color)


class ScoreSetCommand(CANCommand):
    def __init__(self, board, score):
        super(ScoreSetCommand, self).__init__(board, 0)
        self.feature_type = Feature.score_display
        self.msg_type = 0
        self.data = struct.pack('>i', score)


class SwitchRequestStatusCommand(CANCommand):
    def __init__(self, board, switch):
        super(SwitchRequestStatusCommand, self).__init__(board, switch)
        self.feature_type = Feature.switch
        self.msg_type = 0
        self.request = True


class TextSetCommand(CANCommand):
    '''Class for sending text to the 7 segment displays

    Each segment corresponds to a bit in a command byte, with up to 8 bytes per
    message. The mapping of bits to segments is shown below. Bit 7 is the
    period at the bottom right of a 7-segment element.

          --6--
         |     |
         1     5
         |     |
          --0--
         |     |
         2     4
         |     |
          --3-- 7


    '''
    character_lut = {
        ' ': 0x00,
        '0': 0x7e,
        '1': 0x30,
        '2': 0x6d,
        '3': 0x79,
        '4': 0x33,
        '5': 0x5b,
        '6': 0x5f,
        '7': 0x70,
        '8': 0x7f,
        '9': 0x7b,
        'a': 0x77,
        'b': 0x1F,
        'c': 0x4E,
        'd': 0x3D,
        'e': 0x4F,
        'f': 0x47,
        'g': 0x7B,
        'h': 0x17,
        'i': 0x06,
        'j': 0x38,
        'l': 0x0E,
        'n': 0x15,
        'o': 0x7E,
        'p': 0x67,
        'q': 0x73,
        'r': 0x05,
        's': 0x5B,
        't': 0x46,
        'u': 0x1C,
        'v': 0x1C,
        'y': 0x3B,
        '.': 0x80
    }

    def __init__(self, board, text):
        super(TextSetCommand, self).__init__(board, 0)
        self.feature_type = Feature.score_display
        self.msg_type = 2
        self.data = self.convert_text(self.pad_text(text))

    def pad_text(self, text):
        text_len = len(text[:8])
        return (' ' * (8 - text_len)) + text[:8]

    def convert_text(self, text):
        return bytes(self.character_lut[char] for char in text)
