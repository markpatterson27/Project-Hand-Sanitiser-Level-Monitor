# Docker MQTT-SQL Forwarder

Docker container with python script that forwards MQTT messages into an SQL database.

The forwarder script subsribes to all messages on a given base topic. The forwarder then filters and processes received messages, before writing data points to an SQL database.

<br />

## MQTT Message Structure

Received MQTT messages are expected to be structured as follows. The forwarder script will need to be modified if different structured messages are needed.

### MQTT Topics

All messages on the base topic are subscribed to: i.e. `BASE_TOPIC+'/#'`. The following sub-topics are processed. All other sub-topics are ignored.

| Topic | Description |
| --- | --- |
| last child topic: `/sensor-reading` | Any message with the last child topic of `sensor-reading`. |
|  |  |

<br />

### MQTT Payload

The MQTT payload is expected to be in the format:

```js
payload {
    "timestamp": "<timestamp of reading>",
    "meta-data": {
        // this is data that doesn't need to be graphed or processed,
        // but could be used for filtering
        // this data is likely to be strings and unlikely to be numerical
        "<dictionary of meta-data associated with sensor reading>"
    },
    "measures": {
        // this is data that will be processed and/or graphed
        // this data will be numerical
        "<dictionary of sensor readings>"
    }
}
```

## SQL Data Rows

Sensor values are written into a `SensorReadings` table. MQTT message payloads have to be specifically mapped to SQL columns.

**Table structure:**  
| Column | Description |
| --- | --- |
| Id | Auto-generated Id number. Primary key|
| Datestamp | Date and time of reading |
| Device | Id of device taking reading |
| Location | Location of device |
| Method | Method used to gather sensor readings |
| CapacitanceFullLength | Capacitance value of full length foil strips |
| CapacitanceTop | Capacitance value of short foil strips  at top of measurement level |
| CapacitanceBottom | Capacitance value of short foil strips  at bottom of measurement level |
| CapacitanceCallibrated | Value generated from full length reading divided by difference between top and bottom readings |
| BatteryLevel | Voltage level reading of battery |

<br />

**Example data:**  
| Id | Datestamp | Device | Location | Method | CapacitanceFullLength | CapacitanceTop | CapacitanceBottom | CapacitanceCallibrated | BatteryLevel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2020-10-17 10:00:00 | ESP32-abc | somewhere | multipoint | 450 | 400 | 460 | 7.5 | 3.9 |
| 2 | 2020-10-17 10:01:00 | ESP32-xyz | somewhere | single | 250 |  |  |  | 3.7 |

<br />

## References

- https://pypi.org/project/paho-mqtt/
- https://github.com/mkleehammer/pyodbc
