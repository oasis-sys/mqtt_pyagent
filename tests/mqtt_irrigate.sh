#!/bin/bash

DEVICE_NET_NUMBER=$1
TIME_IN_SECONDS=$2

LOG_FILE=/tmp/mqtt_bridge.log
VALVE=1

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters"
    exit 1
fi

time=$TIME_IN_SECONDS
CURRENT_TIME=$(date '+%F %T')
echo $CURRENT_TIME $0 $@ | tee -a $LOG_FILE

#mosquitto_sub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/resp" -u $MQTT_USERNAME -P $MQTT_PASSWORD -W $(($time + 15)) 2> /dev/zero &
mosquitto_sub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/resp" -u $MQTT_USERNAME -P $MQTT_PASSWORD -W $(($time + 9)) 2>/dev/zero | tee -a $LOG_FILE &

echo "$CURRENT_TIME Start irrigation on Line# $VALVE" | tee -a $LOG_FILE
mosquitto_pub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/cmd" -m "S$VALVE   Z" -u $MQTT_USERNAME -P $MQTT_PASSWORD
while [ $time -gt 0 ]; do
    echo -n -e "    \r$time\r"
    ((time=$time - 1))
    sleep 1
done
CURRENT_TIME=$(date '+%F %T')
echo "$CURRENT_TIME Time $TIME_IN_SECONDS seconds is done. Line# $VALVE close irrigarion." | tee -a $LOG_FILE

mosquitto_pub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/cmd" -m "U$VALVE   Z" -u $MQTT_USERNAME -P $MQTT_PASSWORD
echo "Response from device..."
sleep 7
# mosquitto_pub -h $MQTT_SERVER -p 1883 -t "hass_A515C0DE/irrcon0A515_$DEVICE_NET_NUMBER/cmd" -m "GS   Z" -u $MQTT_USERNAME -P $MQTT_PASSWORD
# sleep 4
./mqtt_devstatus.sh $1

