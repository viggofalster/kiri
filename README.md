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

Add binary to PATH:

```sh
sudo ln -s /root/kiri/kiri_usb /usr/bin
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
@reboot python3 /root/kiri/kiri.py >>/var/log/kiri.log
```
