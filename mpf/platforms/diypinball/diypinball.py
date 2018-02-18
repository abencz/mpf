import asyncio
import logging
import threading
import queue
import time

from mpf.core.platform import SwitchPlatform, DriverPlatform, LightsPlatform
from mpf.platforms.interfaces.light_platform_interface import LightPlatformInterface

from .feature import Feature
from .can_device import CANDevice
from .can_event import CANEvent
from .can_command import SwitchRequestStatusCommand

from .rules import PulseOnHitRule, PulseOnHitAndReleaseRule, PulseOnHitAndEnableAndReleaseRule

from .driver import Driver
from .switch import Switch
from .matrix_light import MatrixLight
from .rgb_led import RGBLED, RGBLEDChannel


class HardwarePlatform(SwitchPlatform, DriverPlatform, LightsPlatform):
    def __init__(self, machine):
        super(HardwarePlatform, self).__init__(machine)

        self.log = logging.getLogger('Platform.DIYPinball')
        self.log.info('Configuring DIYPinball hardware')

        self.can = None
        self.switches = {}
        self.leds = {}
        self.checking_switch_state = False

    @asyncio.coroutine
    def initialize(self):
        self.config = self.machine.config['diypinball']
        self.machine.config_validator.validate_config('diypinball', self.config)

        if self.config['debug']:
            self.debug = True

        self.can = CANDevice(self.config['can_device'])
        self.debug_log('Attached to CAN interface {0}'.format(self.config['can_device']))

        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()
        self.send_thread = threading.Thread(target=self._send_loop)
        self.recv_thread = threading.Thread(target=self._recv_loop)
        self.send_thread.daemon = True
        self.recv_thread.daemon = True
        self.send_thread.start()
        self.recv_thread.start()

    def stop(self):
        self.can.close()

    def tick(self):
        while not self.recv_queue.empty():
            self.process_can_event(self.recv_queue.get(False))

        for led in self.leds.values():
            led.update_state()

    def process_can_event(self, event):
        if event.feature_type == Feature.switch:
            self.debug_log(str(event))
            if event.hw_id in self.switches:
                self.switches[event.hw_id].process_event(event)

            if not self.checking_switch_state:
                self.machine.switch_controller.process_switch_by_num(state=event.data[0],
                                                                     num=event.hw_id,
                                                                     platform=self)

    def send(self, cmd):
        self.send_queue.put(cmd)

    def _recv_loop(self):
        while True:
            self.recv_queue.put(self.can.recv())

    def _send_loop(self):
        while True:
            cmd = self.send_queue.get()
            try:
                self.can.send(cmd)
            except OSError:
                self.send_queue.put(cmd)
                time.sleep(0.001)


    """ Switch Interface """
    def configure_switch(self, number, config, platform_settings):
        self.log.info('configuring switch {}'.format(number))
        switch = Switch(self, config, number)
        self.switches[switch.number] = switch
        return switch

    @asyncio.coroutine
    def get_hw_switch_states(self):
        self.checking_switch_state = True
        for switch in self.switches.values():
            self.send(SwitchRequestStatusCommand(switch.board, switch.switch))
        update_time = 0.005 * len(self.switches)
        time.sleep(update_time)
        self.tick()
        self.checking_switch_state = False
        return {switch.number: switch.state for switch in self.switches.values()}

    """ Driver Interface """
    def configure_driver(self, config, number, platform_settings):
        return Driver(self, config, number)

    def clear_hw_rule(self, switch, coil):
        switch.hw_switch.remove_rule(coil.hw_driver)

    def set_pulse_on_hit_and_release_rule(self, enable_switch, coil):
        enable_switch.hw_switch.add_rule(PulseOnHitAndReleaseRule(coil.hw_driver))
        self.log.info('set_pulse_on_hit_and_release_rule called' + repr(enable_switch) + repr(coil))

    def set_pulse_on_hit_and_enable_and_release_rule(self, enable_switch, coil):
        enable_switch.hw_switch.add_rule(PulseOnHitAndEnableAndReleaseRule(coil.hw_driver))
        self.log.info('set_pulse_on_hit_and_enable_and_release_rule called' + repr(enable_switch) + repr(coil))

    def set_pulse_on_hit_and_enable_and_release_and_disable_rule(self, enable_switch, disable_switch, coil):
        self.log.info('set_pulse_on_hit_and_enable_and_release_and_disable_rule called')

    def set_pulse_on_hit_rule(self, enable_switch, coil):
        enable_switch.hw_switch.add_rule(PulseOnHitRule(coil.hw_driver))
        self.log.info('set_pulse_on_hit_rule called')

    """ Light Interface """
    def parse_light_number_to_channels(self, number: str, subtype: str):
        """Parse light channels from number string."""
        return [
            {
                "number": number
            }
        ]

    def configure_light(self, number, subtype, platform_settings) -> LightPlatformInterface:
        self.log.info('configuring light {}, subtype {}'.format(number, subtype))
        try:
            number, channel = number.split("/")
        except ValueError:
            number = number
            channel = None

        if channel is None:
            return MatrixLight(self, number)
        else:
            if number not in self.leds:
                self.leds[number] = RGBLED(self, number)

            led = self.leds[number]
            led_channel = RGBLEDChannel(led, channel)

            return led_channel
