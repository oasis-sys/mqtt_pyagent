#!/usr/bin/python

import sys
import pyudev
import serial

def is_usb_serial(device, vid=None, pid=None, vendor=None, serial=None):
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

def find_communicator_port():
    port_name = None
    context = pyudev.Context()
    for device in context.list_devices(subsystem='tty'):
        if is_usb_serial(device, vid="abcd", pid="1234"):
            print("Port    {}".format(device.device_node))
            # print("Vendor: {} - {}:{}".format(device.properties['ID_VENDOR'], device.properties['ID_VENDOR_ID'], device.properties['ID_MODEL_ID']))
            # print("Serial: {}".format(device.properties['ID_SERIAL_SHORT']))
            port_name = device.device_node
    return port_name

def get_communicator_version(comm_port):
    # Set DTR to Comm Config Mode
    comm_port.setDTR(0)
    comm_port.flushInput()
    comm_port.write(b'~GETVER')
    # str_ret_code = ser.read(32)
    str_ret_code = comm_port.readline()
    # print('Response: {}'.format(str_ret_code.decode('Ascii')))
    # Set DTR to Comm Normal / RF Mode
    comm_port.setDTR(1)
    return str_ret_code

#### send_generic_cmd(oasis_port, str_device_id, str_command)
# oasis_port - serial port device
# str_device_id - Wireless Network Device ID as string
# str_command - Command in String format
def send_generic_cmd(oasis_port, str_device_id, str_command):
    dev_id = int(str_device_id, base=16)
    oasis_port.flushInput()
    package = bytearray(b'\x7E\x08\x00')
    package.extend(str_command.encode('ascii'))
    package[1] = len(package) - 1
    package[2] = dev_id
    # print(' '.join('{:02X}'.format(x) for x in package))
    oasis_port.write(package)
    str_ret_code = oasis_port.readline()
    # print("{}".format(str_ret_code))
    return str_ret_code

def get_valve_controller_status(str_device_id, oasis_port):
    dev_id = int(str_device_id)
    oasis_port.flushInput()
    package = bytearray(b'\x7E\x08\x00GS   Z')
    package[2] = dev_id
    # print(' '.join('{:02x}'.format(x) for x in package))
    oasis_port.write(package)
    str_ret_code = oasis_port.readline()
    # print("{}".format(str_ret_code))
    return str_ret_code

def set_valve_in_controller(str_device_id, set_valve_state, valve_number, oasis_port):
    dev_id = int(str_device_id)
    valve_id = int(valve_number)
    valve_state = ord(set_valve_state)
    oasis_port.flushInput()
    package = bytearray(b'\x7E\x08\x00_    Z')
    # package_byte_array = bytearray(package, encoding='ascii')
    package[2] = dev_id
    package[4] = valve_id + 48
    package[3] = valve_state
    # print(' '.join('{:02x}'.format(x) for x in package))
    oasis_port.write(package)
    str_ret_code = oasis_port.readline()
    # print("{}".format(str_ret_code))
    return str_ret_code

def open_port(port_file):
    SerialPort = serial.Serial()
    SerialPort.baudrate = 115200
    SerialPort.port = port_file
    SerialPort.stopbits = serial.STOPBITS_ONE
    SerialPort.rtscts = False
    SerialPort.xonxoff = False
    SerialPort.dsrdtr = False
    SerialPort.timeout = 1
    try:
        SerialPort.open()
    except:
        print("Error opening port")
        sys.exit(1)
    return SerialPort
