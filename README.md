# KIRI - Keyboard Interception, Remapping and Injection using Raspberry Pi as a HID Proxy.

Near limitless abilities for a keyboard warrior.

## Features

* Simple remap of any key or key combination to any key or key combination.
* Build keyboard mapping and/or macros using python.
* Completely external and thereby supports any operating system capable of receiving keyboard input via USB.

## Hardware Requirements

* A Raspberry Pi with an USB OTG port (e.g. Pi 4 and Zero W) - this is required so the Raspberry Pi may identify itself
  as a Human Interface Device (HID).
* An additional USB port for keyboard input to the Raspberri Pi. Only if using a bluetooth keyboard the Raspberri Pi
  Zero W will suffice, otherwise a Raspberri Pi 4 is needed.

## OS Requirements

* Testing has only been conducted with Raspberrian OS - other distributions may work also.
* For convenience and later modifications one can enable sshd on the raspberry pi and connect it to e.g. WiFi-LAN.

## Software Requirements
* python >= 3.4 with evdev and importlib installed (pip3 install evdev importlib)

## Install

### Enable USB OTG via the dwc2 module and allow us to register a HID device in non-kernel mode

```sh
sudo -i
echo "dtoverlay=dwc2" | tee -a /boot/config.txt
echo "dwc2" | tee -a /etc/modules
echo "libcomposite" | tee -a /etc/modules
```

```sh
touch /usr/bin/kiri_usb
chmod +x /usr/bin/kiri_usb
nano /usr/bin/kiri_usb
```

Add the following content - save and close the file afterwards.

```sh
#!/bin/bash
# Sourced and modified based on from: https://www.isticktoit.net/?p=1383
cd /sys/kernel/config/usb_gadget/
mkdir -p heck_hid_proxy_keyb
cd heck_hid_proxy_keyb
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB # USB2
mkdir -p strings/0x409=
echo "2021080700000001" > strings/0x409/serialnumber
echo "KIRI" > strings/0x409/manufacturer
echo "KIRI (HID USB Proxy Device)" > strings/0x409/product
mkdir -p configs/c.1/strings/0x409
echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# Add functions here
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length

# usb descriptor equivalent to keybrd.hid seen with https://www.usb.org/document-library/hid-descriptor-tool
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc

ln -s functions/hid.usb0 configs/c.1/
# End functions

ls /sys/class/udc > UDC
```

Modify /etc/rc.local to call the script on boot.

```sh
nano /etc/rc.local
```

Insert the following before exit 0.

```sh
/usr/bin/kiri_usb
```

Reboot the device.

```sh
reboot
```

After reboot, verify that /dev/hidg0 exists.

```sh
ls /dev/hidg0
```

The Raspberry Pi is now setup so e.g. a python script can write USB reports to the USB OTG port by simply writing to
/dev/hidg0.


### Installing KIRI

1. Using git, checkout to a folder accessible by a super-user, e.g. /root/kiri.
</br>or
2. Copy the files of this repository to e.g. /root/kiri
3. You should now have a file with the following path: /root/kiri/kiri.py on the raspberry pi.

Set up a service or e.g. crontab to run kiri.py on boot as a super-user (e.g. root).

## Example with crontab
```sh
sudo -i
crontab -e
```
Add the following line

```
@reboot python3 /root/kiri/kiri.py
```
