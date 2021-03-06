# Project: Hand Sanitiser Level Monitor

![MicroPython Code Tests](https://github.com/markpatterson27/Project-Hand-Sanitiser-Level-Monitor/workflows/MicroPython%20Code%20Tests/badge.svg)
![Stack-Integration-Test](https://github.com/markpatterson27/Project-Hand-Sanitiser-Level-Monitor/workflows/Stack-Integration-Test/badge.svg)

IoT project looking at possible ways to measure the level of hand sanitiser left at sanitiser stations.

![dataflow diagram](assets/Dataflow-Diagram-embed-solid-3.svg)

![proof of concept bottle and dashboard](assets/poc-bottle-dashboard.png)

<br>

## Files and Folders

| File/Folder | Description |
|--- | --- |
| docker-compose-stack/ | Docker compose project |
| micropython/ | sync folder for micropython devices |
| micropython/cap_reading.py | micropython script that regularly reads capacitance and battery level and sends the data to a mqtt server. |
| micropython/level-test.py | micropython script that reads capacitance levels and displays a bar graph on a terminal screen. |
| mp-tests/ | folder for test files testing micropython project |
| powerbi-dasboards/ | some simple Power BI dashboards graphing data from the SQL Server container |
|  |  |

<br>

## Branches

**master**: main branch.  

<br>

## Configuration

### MQTT Topics

| MQTT Topic | Description |
| --- | --- |
| hand-sanitiser-levels/ | base topic for project |
| hand-sanitiser-levels/messages | topic for status messages |
| hand-sanitiser-levels/{client-id}/sensor-reading | sensor readings published on this topic as json |
| hand-sanitiser-levels/{client-id}/messages | topic for sending messages to devices |
| hand-sanitiser-levels/{client-id}/messages/led | topic to control on device led. payload should be a string and one of `on`, `off`, or `blink`. |
| hand-sanitiser-levels/{client-id}/messages/location | set the devices location. payload should be a string. |
| hand-sanitiser-levels/{client-id}/messages/poll-interval | topic to set poll interval on device. payload should be an integer. |
| hand-sanitiser-levels/{client-id}/messages/polling-hours | topic to set polling hours on device. payload should be json with following keys: `{'start': start hour, 'end': ending hour}`. hours should be integers. |
|  |  |

### Ports

Some of the docker services are mapped to non-standard ports.

| Port | Service |
|---|---|
| 123 | NTP |
| 1433 | SQL Server |
| 1883 | MQTT Broker |
| 3000 | Grafana |

<br>

### Database

| Database | HandSanitiserLevels |
|---|---|
| Tables/Measures | sensor-readings |
| Retention Policies: | 2_weeks (default) |
|  | 4_years |
| Continuous Queries: | cq_1h - `mean(*) INTO 4_years FROM 2_weeks GROUP BY time(60m), *` |

<br>

## Circuit Diagram - Single Wire
Wire the components as shown in the diagram. Place the other end of the wire on the liquid volume to be measured.

<!-- ![circuit diagram](assets/###-circuit-diagram_schem.svg) -->

#### Components Needed
* wire
* ESP32 dev board (Lolin D32)

<br />

![breadboard diagram](assets/lolin-d32-wire-capacitance-circuit-diagram_bb.png)

<br />

### Default Pin Wiring

| Pin No | Function | Device Connection |
| --- | --- | --- |
| 27 | GPIO27/Touch7 | Wire strand |
|  |  |  |

<br />

## Circuit Diagram - Multi-Point Foil Strips
Wire the components as shown in the diagram. Place the other end of the wire on the liquid volume to be measured.

<!-- ![circuit diagram](assets/###-circuit-diagram_schem.svg) -->

#### Components Needed
* wire
* foil tape
* ESP32 dev board (Lolin D32)


<br />

![breadboard diagram](assets/lolin-d32-multi-point-capacitance-circuit-diagram_bb.png)

<br />

### Default Pin Wiring

| Pin No | Function | Device Connection |
| --- | --- | --- |
| 13 | GPIO13/Touch4 | Full height strip |
| 12 | GPIO12/Touch5 | Top strip |
| 14 | GPIO14/Touch6 | Bottom strip |
|  |  |  |

<br />

![pin diagram](assets/d32_pro_v2-pinout.jpg)


<br />

## Level Test

This test was performed to determine if there was enough change in capacitance between full and empty to be able to reliably determine the level of sanitiser in the container. The script [level_test.py](micropython/level_test.py) was used. This script measures capacitance on a foil script, self-calibrating maximum and minimum readings, then calculates a percentage level for the current reading. This level is displayed on the serial connection as a bar graph.

![level test gif](assets/level-test.gif)

<br />

## References

- Testing stubs: https://github.com/tflander/esp32-machine-emulator
