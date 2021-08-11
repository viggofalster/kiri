# Copyright 2021 by Viggo Falster (https://github.com/viggofalster)
# All rights reserved.
# This file is part of KIRI - Keyboard Interception, Remapping and Injection using Raspberry Pi as a HID Proxy,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import importlib
import logging
import sys
import evdev
import time
from evdev import InputDevice, categorize, ecodes
from hid_keys import hid_key_map as hid_keys
import config


class Kiri:
    def __init__(self):
        self.log = logging.getLogger()
        self.default_log_level = logging.INFO
        self.log.setLevel(level=self.default_log_level)
        self.log_handler = logging.StreamHandler(sys.stdout)
        self.log_handler.setLevel(logging.DEBUG)
        self.log_formatter = logging.Formatter('[%(asctime)s|%(name)s|%(levelname)s] %(message)s')
        self.log_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.log_handler)

        self.configuration = config.Config()

        self.input_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for input_device_no, input_device in enumerate(self.input_devices):
            self.log.info('Found device: %d, %s, %s, %s', input_device_no, input_device.path, input_device.name,
                          input_device.phys)

        self.device = None
        while self.device is None:
            try:
                self.device = InputDevice('/dev/input/event0')
            except:
                self.log.info("No keyboard - waiting...")
                time.sleep(5)

        self.log.info('Grabbing device: %s, %s, %s', self.device.path, self.device.name, self.device.phys)

        # grab provides exclusive access to the device
        self.device.grab()

        self.modifiers = {'KEY_LEFTCTRL': 0, 'KEY_LEFTSHIFT': 1, 'KEY_LEFTALT': 2, 'KEY_LEFTMETA': 3,
                          'KEY_RIGHTCTRL': 4, 'KEY_RIGHTSHIFT': 5, 'KEY_RIGHTALT': 6, 'KEY_RIGHTMETA': 7}
        self.modifier: chr = 0b00000000
        self.pressed_keys = set()

        self.is_caps_active = False
        self.is_right_alt_active = False
        self.is_debug_logging_active = False
        self.is_active = True
        self.log.info('Activated - ready for key processing')

    def reset(self):
        try:
            self.modifier: chr = 0b00000000
            self.pressed_keys = set()
            self.write_report(chr(0) * 8)
        except Exception as e:
            self.log.error('Failed to reset: %s', str(e))

    def run(self):
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY:
                try:
                    data = categorize(event)

                    emit, keycode, keystate = self.configuration.remap_intercept(kiri=self, data=data)

                    if emit is False:
                        continue

                    if keycode in self.modifiers:
                        self.update_modifier(keycode, keystate)
                    else:
                        if keystate == 0:
                            self.release(keycode)

                        if keystate == 1:
                            self.press(keycode)

                        if keystate == 2:
                            # ignore update
                            continue
                        #     self.release(keycode)
                        #     self.press(keycode)

                except Exception as e:
                    self.log.error('run loop error: %s', e, exc_info=True)
                    self.reset()

    def reload_config(self):
        self.log.info('reloading config begin')
        importlib.reload(config)
        self.configuration = config.Config()
        self.log.info('reloading config end')

    def toggle_debug_logging(self):
        if self.is_debug_logging_active:
            self.is_debug_logging_active = False
            self.log.setLevel(level=self.default_log_level)
        else:
            self.is_debug_logging_active = True
            self.log.setLevel(level=logging.DEBUG)

    def update_modifier(self, keycode, keystate):
        if keystate == 0:
            self.modifier = self.clear_bit(self.modifier, self.modifiers[keycode])
            self.update_state()
        if keystate == 1:
            self.modifier = self.set_bit(self.modifier, self.modifiers[keycode])
            self.update_state()

    def update_state(self):
        pressed_chars = ''.join([chr(hid_keys[pressed_key]) for pressed_key in self.pressed_keys][:6])
        self.write_report(chr(self.modifier) + chr(0) + pressed_chars + chr(0) * (6 - len(pressed_chars)))

    def release(self, keycode):
        if keycode in self.pressed_keys:
            self.pressed_keys.remove(keycode)
            self.update_state()

    def press(self, keycode):
        if keycode not in self.pressed_keys:
            self.pressed_keys.add(keycode)
            self.update_state()

    def write_report(self, report: str):
        self.log.debug('Writing report to output: %s', ":".join("{:02x}".format(c) for c in report.encode('utf-8')))
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(report.encode())

    @staticmethod
    def set_bit(value, bit):
        return value | (1 << bit)

    @staticmethod
    def clear_bit(value, bit):
        return value & ~(1 << bit)


if __name__ == "__main__":
    kiri = Kiri()
    kiri.run()
