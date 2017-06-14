#!/usr/bin/python

import usb.core
import usb.util
from time import sleep

TOYPAD_INIT = [0x55, 0x0f, 0xb0, 0x01, 0x28, 0x63, 0x29, 0x20, 0x4c, 0x45, 0x47, 0x4f, 0x20, 0x32, 0x30, 0x31, 0x34, 0xf7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

OFF   = [0,0,0]
RED   = [255,0,0]
GREEN = [0,255,0]
BLUE  = [0,0,255]

ALL_PADS   = 0
CENTER_PAD = 1
LEFT_PAD   = 2
RIGHT_PAD  = 3

# Actions
TAG_INSERTED = 0
TAG_REMOVED  = 1

# UIDs can be retrieved with Android App (most probably in hexadecimal)
uidDarthVader = (4, 161, 158, 210, 227, 64 , 128) # Darth Vader from Disney Infinity 3.0


def init_usb():
    global dev

    dev = usb.core.find(idVendor=0x0e6f, idProduct=0x0241)

    if dev is None:
        print 'Device not found'
    else:
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

        print usb.util.get_string(dev, dev.iProduct)

        dev.set_configuration()
        dev.write(1,TOYPAD_INIT)

    return dev


def send_command(dev,command):

    # calculate checksum
    checksum = 0
    for word in command:
        checksum = checksum + word
        if checksum >= 256:
            checksum -= 256
        message = command+[checksum]

    # pad message
    while(len(message) < 32):
        message.append(0x00)

    # send message
    dev.write(1, message)

    return


def switch_pad(pad, colour):
    send_command(dev,[0x55, 0x06, 0xc0, 0x02, pad, colour[0], colour[1], colour[2],])
    return


def uid_compare(uid1, uid2):
    match = True
    for i in range(0,7):
        if (uid1[i] != uid2[i]) :
            match = False
    return match 


def main():
    init_usb()
    if dev != None :
        while True:
            try:
                in_packet = dev.read(0x81, 32, timeout = 10)
                bytelist = list(in_packet)

                if not bytelist:
                    pass
                elif bytelist[0] != 0x56: # NFC packets start with 0x56
                    pass
                else:
                    pad_num = bytelist[2]
                    uid_bytes = bytelist[6:13]
                    match = uid_compare(uid_bytes, uidDarthVader)
                    action = bytelist[5]
                    if action == TAG_INSERTED :
                        if match:
                            # Darth Vader
                            switch_pad(pad_num, RED)
                        else:
                            # some other tag
                            switch_pad(pad_num, GREEN)
                    else:
                        # some tag removed
                        switch_pad(pad_num, OFF)

            except usb.USBError, err:
                pass

        switch_pad(ALL_PADS,OFF)
    return

if __name__ == '__main__':
    main()
  
