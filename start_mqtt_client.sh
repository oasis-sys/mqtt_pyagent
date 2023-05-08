#!/bin/bash

python3 wireless2mqtt.py -H $MQTT_SERVER -f config_user.json -u $MQTT_USERNAME -p $MQTT_PASSWORD
if [ $? -ne 0 ]; then
    echo "Error connection to server."
    exit 1
fi

