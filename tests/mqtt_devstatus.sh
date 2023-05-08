#!/bin/bash

DEVICE_NET_NUMBER=$1
LOG_FILE=/tmp/mqtt_bridge.log

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
    exit 1
fi

CURRENT_TIME=$(date '+%F %T')
echo $CURRENT_TIME $0 $@ | tee -a $LOG_FILE

mosquitto_sub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/resp" -u $MQTT_USERNAME -P $MQTT_PASSWORD -W 8 2>/dev/zero | xargs -d '\n' -I {} date '+%F %T {}' | tee -a $LOG_FILE &
mosquitto_pub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/cmd" -m "GS   Z" -u $MQTT_USERNAME -P $MQTT_PASSWORD
sleep 5

