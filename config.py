# Copyright 2021 by Viggo Falster (https://github.com/viggofalster)
# All rights reserved.
# This file is part of KIRI - Keyboard Interception, Remapping and Injection using Raspberry Pi as a HID Proxy,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from kiri import Kiri


class Config:
    def remap_intercept(self, kiri: Kiri, data):
        scancode = data.scancode
        keycode = data.keycode
        keystate = data.keystate
        emit = True

        kiri.log.debug('Intercept begin. %s: %d', keycode, keystate)

        if keycode == 'KEY_CAPSLOCK':
            emit = False
            if keystate == 0:
                kiri.is_caps_active = False
                kiri.reset()  # prevent remapped keys from hanging
            if keystate == 1:
                kiri.is_caps_active = True

        # special consideration for toggling active state
        if kiri.is_caps_active:
            if keycode == 'KEY_ESC' and keystate == 1:
                if kiri.is_active:
                    kiri.device.ungrab()
                    kiri.is_active = False
                else:
                    kiri.device.grab()
                    kiri.is_active = True

                kiri.log.debug('Is active: %s', str(kiri.is_active))
                return False, None, None

            if keycode == 'KEY_SYSRQ':
                if keystate == 1:
                    kiri.toggle_debug_logging()
                return False, None, None

            if keycode == 'KEY_HOME' and keystate == 1:
                kiri.reload_config()
                return False, None, None

        if not kiri.is_active:
            return False, None, None

        # if keycode == 'KEY_RIGHTALT':
        #     if keystate == 0:
        #         proxy.is_right_alt_active = False
        #     if keystate == 1:
        #         proxy.is_right_alt_active = True

        if kiri.is_caps_active:

            if keycode == 'KEY_T':
                keycode = 'KEY_INSERT'

            if keycode == 'KEY_8':
                keycode = 'KEY_BACKSLASH'
            if keycode == 'KEY_9':
                keycode = 'KEY_LEFTBRACE'                
            if keycode == 'KEY_0':
                keycode = 'KEY_RIGHTBRACE'                
            if keycode == 'KEY_Y':
                keycode = 'KEY_ESC'
            if keycode == 'KEY_U':
                keycode = 'KEY_HOME'
            if keycode == 'KEY_I':
                keycode = 'KEY_UP'
            if keycode == 'KEY_O':
                keycode = 'KEY_END'
            if keycode == 'KEY_P':
                keycode = 'KEY_PAGEUP'
            if keycode == 'KEY_J':
                keycode = 'KEY_LEFT'
            if keycode == 'KEY_K':
                keycode = 'KEY_DOWN'
            if keycode == 'KEY_L':
                keycode = 'KEY_RIGHT'
            if keycode == 'KEY_SEMICOLON':
                keycode = 'KEY_PAGEDOWN'
            if keycode == 'KEY_H':
                keycode = 'KEY_BACKSPACE'
            if keycode == 'KEY_N':
                keycode = 'KEY_DELETE'
            if keycode == 'KEY_M':
                keycode = 'KEY_ENTER'

        kiri.log.debug('Intercept end. %s: %d', keycode, keystate)

        return emit, keycode, keystate
