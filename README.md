# OASIS MQTT Agent

Compatible with Linux PC's, Raspberry Pi running on Raspbian, other single board PC's running Linux based OS's

## Runtime Dependencies

```bash
sudo pip3 install pyudev pySerial paho-mqtt logging journal systemd
```

## Work with Source Code

### Clone Source Repo

```bash
git clone git@github.com:oasis-sys/mqtt_pyagent.git
```

### Development Submodules

```bash
git submodule update --init --recursive
cd paho.mqtt.python/
sudo python3 setup.py install
```

### Dependencies required for running tests

```bash
sudo apt install -y mosquitto-clients
```

## Agent config.json example

```bash
{
  "json_ver": 1,
  "host": "server_ip",
  "irrcon0A515": [
       "10",
       "11"
  ],
  "user_id": "A5151DEA",
  "boolean": true,
  "color": "gold"
}
```

## Usage

Define environment variables MQTT_USERNAME and MQTT_PASSWORD

Running the client

```bash
MQTT_USERNAME=your_mqtt_user MQTT_PASSWORD=your_mqtt_password ./start_mqtt_client.sh
```

## Example of /etc/default/oasis_settings

```bash
MQTT_SERVER=<MQTT Service IP address>
MQTT_USERNAME=<Your MQTT Username>
MQTT_PASSWORD=<Your MQTT Password>
```

----

## [Tests](tests/README.md)

----

## Usefull Links

[Python MQTT Client](https://pypi.org/project/paho-mqtt/)

[CDC ACM Windows 32/64 Driver](https://www.kernel.org/doc/Documentation/usb/linux-cdc-acm.inf)
