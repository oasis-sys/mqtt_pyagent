# Tests

oasis_tech_cdc.inf - Windows driver

silabs-cdc.cat - Windows 8/10 driver

## Local test of communicator

```bash
python3 tests/test_comm_ver.py
```

## Test via cloud MQTT services

Before using the test scripts please add following settings into .bashrc file

```bash
export MQTT_SERVER=<MQTT Service IP address>
export MQTT_USERNAME=<Your MQTT Username>
export MQTT_PASSWORD=<Your MQTT Password>
```

Then restart your terminal in order to renew environment variables and try test scripts such as:

```bash
./mqtt_devstatus.sh 23
```

where: 23 - hexadecimal device number

```bash
./mqtt_irrigate.sh 23 600
```

where: 600 - time in seconds for irrigation
