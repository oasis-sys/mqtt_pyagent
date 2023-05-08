#!/usr/bin/python

import pyudev
import sys
import time
import serial

def is_usb_serial(device, vid=None, pid=None, vendor=None, serial=None, *args,
                  **kwargs):

    if 'ID_VENDOR' not in device.properties:
        return False
    if vid is not None:
        if device.properties['ID_VENDOR_ID'] != vid:
            return False
    if pid is not None:
        if device.properties['ID_MODEL_ID'] != pid:
            return False
    if vendor is not None:
        if 'ID_VENDOR' not in device.properties:
            return False
        if not device.properties['ID_VENDOR'].startswith(vendor):
            return False
    if serial is not None:
        if 'ID_SERIAL_SHORT' not in device.properties:
            return False
        if not device.properties['ID_SERIAL_SHORT'].startswith(serial):
            return False
    return True

def read_communicator_version():
    ser.setDTR(0)
    ser.flushInput()
    ser.write(b'~GETVER ')
    str_ret_code = ser.readline()
    ser.setDTR(1)
    print ("Communicator Version: {}".format(str_ret_code.decode("utf-8")))

def read_controller_version():
    ser.setDTR(1)
    ser.flushInput()
    ser.write(b'~GETVER ')
    str_ret_code = ser.readline()
    print ("Controller Version: {}".format(str_ret_code.decode("utf-8")))

context = pyudev.Context()
for device in context.list_devices(subsystem='tty'):
    if is_usb_serial(device, vid="abcd", pid="1234"):
        print(device.device_node)
        print("Vendor: " + device.properties['ID_VENDOR'] + " VID:PID = " + device.properties['ID_VENDOR_ID'] + ":" + device.properties['ID_MODEL_ID'])
        print("Serial: " + device.properties['ID_SERIAL_SHORT'])
        oasis_comm_node = device.device_node


ser = serial.Serial()
ser.baudrate = 115200
ser.port=oasis_comm_node
ser.stopbits=serial.STOPBITS_ONE
ser.rtscts=False
ser.xonxoff=False
ser.dsrdtr=False
ser.timeout=5

try:
    ser.open()
except:
    sys.exit ("Error opening port")

read_communicator_version()
time.sleep(2)
read_controller_version()

sys.exit(0)


