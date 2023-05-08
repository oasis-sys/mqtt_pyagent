#!/usr/bin/python

import pyudev
import sys
import time
import serial

SerialPortNode = None
SerialPort = None

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

def read_version(port):
    port.setDTR(0)
    port.flushInput()
    port.write(b'~GETVER ')
    str_ret_code = port.readline()
    port.setDTR(1)
    #print ("Communicator Version: {}".format(str_ret_code.decode("utf-8")))
    return "{}".format(str_ret_code.decode("utf-8"))

def read_controller_version(port):
    port.setDTR(1)
    port.flushInput()
    port.write(b'~GETVER ')
    str_ret_code = port.readline()
    print ("Controller Version: {}".format(str_ret_code.decode("utf-8")))

def send_packet(port, packet):
    port.setDTR(1)
    port.flushInput()
    port.write(packet.encode())
    str_ret_code = port.readline()
    return "{}".format(str_ret_code.decode("utf-8"))

def send_byte_packet(port, packet):
    port.setDTR(1)
    port.flushInput()
    port.write(packet)

def detect_port():
    context = pyudev.Context()
    for device in context.list_devices(subsystem='tty'):
        if is_usb_serial(device, vid="abcd", pid="1234"):
            print(device.device_node)
            print("Vendor: " + device.properties['ID_VENDOR'] + " VID:PID = " + device.properties['ID_VENDOR_ID'] + ":" + device.properties['ID_MODEL_ID'])
            print("Serial: " + device.properties['ID_SERIAL_SHORT'])
            return device.device_node

def open_port(port_file):
    SerialPort = serial.Serial()
    SerialPort.baudrate = 115200
    SerialPort.port = port_file
    SerialPort.stopbits = serial.STOPBITS_ONE
    SerialPort.rtscts = False
    SerialPort.xonxoff = False
    SerialPort.dsrdtr = False
    SerialPort.timeout=5
    try:
        SerialPort.open()
    except:
        sys.exit ("Error opening port")
    return SerialPort

# Test
#SerialPortNode = detect_communicator_port()
#if None != SerialPortNode:
#    SerialPort = open_communicator_port(SerialPortNode)
#comm_version = read_communicator_version(SerialPort)
#print("Communicator version".format(comm_version))
#time.sleep(2)
#read_controller_version(SerialPort)
#time.sleep(1)
#sys.exit(0)


