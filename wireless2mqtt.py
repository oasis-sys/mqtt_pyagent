#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import os
import sys
import ssl
import argparse
import time
import requests
import threading
import logging
from systemd import journal
import oasis_devs
import json

IRRCON_DEVICE_TYPE = "irrcon0A515"
UserId = None
oasis_comm_port_node = None
SerialPort = None
VersionCommunicator = None

def is_online(url='http://www.google.com/', timeout=5):
    try:
        req = requests.head(url, timeout=timeout)
        # HTTP errors are not raised by default, this statement does that
        req.raise_for_status()
        return True
    except requests.HTTPError as e:
        logger.info("Checking internet connection failed, status code {0}.".format(e.response.status_code))
    except requests.ConnectionError:
        logger.info("No internet connection available.")
    return False

logger = logging.getLogger("oasis_mqtt")
#logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")

handler = journal.JournaldLogHandler()
# Enable for prints in stdout
# handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('Starting of OASIS MQTT Agent')

parser = argparse.ArgumentParser()

parser.add_argument('-H', '--host', required=False, default="")
parser.add_argument('-f', '--fileconf', required=False, default="config.json")
parser.add_argument('-q', '--qos', required=False, type=int, default=0)
parser.add_argument('-c', '--clientid', required=False, default=None)
parser.add_argument('-u', '--username', required=False, default=None)
parser.add_argument('-d', '--disable-clean-session', action='store_true', help="disable 'clean session' (sub + msgs not cleared when client disconnects)")
parser.add_argument('-p', '--password', required=False, default=None)
parser.add_argument('-P', '--port', required=False, type=int, default=None, help='Defaults to 8883 for TLS or 1883 for non-TLS')
parser.add_argument('-k', '--keepalive', required=False, type=int, default=60)
parser.add_argument('-s', '--use-tls', action='store_true')
parser.add_argument('--insecure', action='store_true')
parser.add_argument('-F', '--cacerts', required=False, default=None)
parser.add_argument('--tls-version', required=False, default=None, help='TLS protocol version, can be one of tlsv1.2 tlsv1.1 or tlsv1\n')
parser.add_argument('-D', '--debug', action='store_true')

args, unknown = parser.parse_known_args()

def device_action(DeviceId, action):
    # print("Valve action - {} {}".format(valve, set_state))
    logger.info("Device ID: {} sent Action: {}".format(DeviceId, action))
    for i in range(0, 7):
        resp = oasis_devs.send_generic_cmd(SerialPort, DeviceId.split('_')[1], action)
        if 0 < len(resp):
            # dev_status = resp.decode("utf-8").rstrip().split(',')
            # print("Status: {}".format(dev_status))
            str_response = resp.decode("utf-8")
            logger.info("Status: {}".format(str_response))
            infot = mqttc.publish("hass_{}/{}/resp".format(UserId, DeviceId), str_response.strip(), 1)
            # infot.wait_for_publish()
            break
 
def mqtt_message_processor(topic, message):
    logger.info("Topic: {}; Mess: {}".format(topic, message))
    top_splited = topic.split('/')
    for topic_item in top_splited:
        print("Topic item: {}".format(topic_item))
    # Forward MQTT message from server to communicator
    thr_x = threading.Thread(target=device_action, args=(top_splited[1], message))
    thr_x.start()

#####################################################################################################
# 0 - success, connection accepted
# 1 - connection refused, bad protocol
# 2 - refused, client-id error
# 3 - refused, service unavailable
# 4 - refused, bad username or password
# 5 - refused, not authorized
def on_connect(mqttc, obj, flags, rc):
    if 0 == rc:
        print("Connected to: {}".format(args.host))
    else:
        print("Error connection to server: {}".format(rc +10))
        sys.exit(rc +10)

def on_message(mqttc, obj, msg):
    mqtt_message_processor(msg.topic, msg.payload.decode("utf-8"))

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

usetls = args.use_tls

if args.cacerts:
    usetls = True

port = args.port    
if port is None:
    if usetls:
        port = 8883
    else:
        port = 1883

mqttc = mqtt.Client(args.clientid,clean_session = not args.disable_clean_session)

# Detect communicator and his version
oasis_comm_port_node = oasis_devs.find_communicator_port()
if None != oasis_comm_port_node:
    SerialPort = oasis_devs.open_port(oasis_comm_port_node)
else:
    logger.info("Error: Cannot to find USB communicator.")
    sys.exit(1)

VersionCommunicator = oasis_devs.get_communicator_version(SerialPort)
logger.info("Communicator Version: {}".format(VersionCommunicator.decode("utf-8")))

if usetls:
    if args.tls_version == "tlsv1.2":
       tlsVersion = ssl.PROTOCOL_TLSv1_2
    elif args.tls_version == "tlsv1.1":
       tlsVersion = ssl.PROTOCOL_TLSv1_1
    elif args.tls_version == "tlsv1":
       tlsVersion = ssl.PROTOCOL_TLSv1
    elif args.tls_version is None:
       tlsVersion = None
    else:
       logger.info("Unknown TLS version - ignoring")
       tlsVersion = None

    if not args.insecure:
        cert_required = ssl.CERT_REQUIRED
    else:
        cert_required = ssl.CERT_NONE
        
    mqttc.tls_set(ca_certs=args.cacerts, certfile=None, keyfile=None, cert_reqs=cert_required, tls_version=tlsVersion)

    if args.insecure:
        mqttc.tls_insecure_set(True)

if args.username or args.password:
    mqttc.username_pw_set(args.username, args.password)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

if args.debug:
    mqttc.on_log = on_log

config_file = args.fileconf
logger.info("Loading configuration from: {}".format(config_file))

with open(config_file) as json_file:
    data = json.load(json_file)

# Wait for Internet connection
time_wait = 0
while False == is_online():
    time.sleep(10)
    time_wait = time_wait + 1
    logger.info("Waiting for Internet connection: {} sec".format(time_wait *10))

logger.info("Internet connection succeed.")

mqttc.connect(args.host, port, args.keepalive)
logger.info("Connected to: " + args.host + " port: " + str(port))

UserId = data['user_id']
logger.info("Defined user ID: ".format(UserId))
logger.info("Added devices:")
for dev in data[IRRCON_DEVICE_TYPE]:
    topic_for_subscribe = "hass_{}/{}_{}/cmd/#".format(UserId, IRRCON_DEVICE_TYPE, dev)
    logger.info("MQTT Subscribe on topic: {}".format(topic_for_subscribe))
    mqttc.subscribe("{}".format(topic_for_subscribe), args.qos)

mqttc.loop_forever()
