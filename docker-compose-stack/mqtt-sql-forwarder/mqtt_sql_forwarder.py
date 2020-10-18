#!/usr/bin/env python3
# script to forward MQTT data to an SQL database

import paho.mqtt.client as mqtt
import pyodbc
import time, datetime
import json
import os

# define constants
MQTT_SERVER = ('mqtt', 1883) # ip, port
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'mqtt')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'password')
BASE_TOPIC = os.getenv('BASE_TOPIC', 'mqtt-sql-stack')
MQTT_CLIENT_ID = 'MQTT-SQL-Forwarder'    # MQTT to SQL forwarder
DB_DRIVER = 'ODBC Driver 17 for SQL Server'
DB_SERVER = ('sqlserver', 1433)   # ip, port
DB_USER = os.getenv('SQL_USERNAME', 'SA')
DB_PASS = os.getenv('SQL_PASSWORD', 'Pa$$w0rd1234')
DB_NAME = os.getenv('SQL_DATABASE', 'MQTTSQLStack')
# DB_TABLE = 'sensor-readings'

db_connection_string = 'DRIVER={{{0}}};SERVER={1},{2};DATABASE={3};UID={4};PWD={5}'.format(
    DB_DRIVER,
    DB_SERVER[0],
    DB_SERVER[1],
    DB_NAME,
    DB_USER,
    DB_PASS
)

subscribe_topic = BASE_TOPIC+'/+/sensor-reading'
incoming_queue = []

def on_connect(client, userdata, flags, rc):
    print("Connected flags: ", str(flags))
    print("Connected with result code: "+str(rc))
    msg = {
        'Connected Client ID': MQTT_CLIENT_ID,
        'Subscribed channel': subscribe_topic,
        'device': 'MQTT to SQL forwarder',
        'message type': 'on-connect'
    }
    client.publish(BASE_TOPIC+'/messages', json.dumps(msg))
    client.subscribe(subscribe_topic)
    print("Subscribed to topic: " + subscribe_topic)

def on_message(client, userdata, msg):
    global incoming_queue
    print("Received a message on topic: " + msg.topic)

    # add topics to be processed to the list
    # pass_topics = ['/sensor-reading']
    
    # strip out base topic
    topic = msg.topic[len(BASE_TOPIC+'/'):]
    
    # only pass sensor-reading topics
    last_child_topic = msg.topic.rsplit('/', 1)[-1]
    if last_child_topic == "sensor-reading": # payload on device/sensor
        print(topic)
        try:
            message = {
                'topic': topic,
                'payload': json.loads(msg.payload)#.decode("utf-8")
            }
            print(message['payload'])
        except TypeError:   # catch invalid json deserialise
            print("Invalid payload Type")
            # raise
        except ValueError:
            print("Invalid payload Value")
            # raise
        else:
            incoming_queue.append(message)

def process_queue():
    '''
    process incoming mqtt messages and return SQL insert statements as strings
    '''
    global incoming_queue
    _queue = incoming_queue
    incoming_queue = []
    db_statement_strings = []

    # per topic queues
    sensor_readings = []

    # process topics into seperate queues
    for message in _queue:
        print("Topic: {}".format(message['topic']))

        last_child_topic = message['topic'].rsplit('/', 1)[-1]

        # add sensor readings if payload contains device id and readings
        if (last_child_topic == "sensor-reading" and isinstance(message['payload'], dict) 
            and all(key in message['payload'].keys() for key in ('meta-data','measures')) 
            and 'device' in message['payload']['meta-data'].keys()
        ):
            sensor_readings.append(message['payload'])


    # process sensor readings
    if sensor_readings:
        db_statement_string = 'INSERT INTO SensorReadings(Datestamp, Device, Location, Method, CapacitanceFullLength, CapacitanceTop, CapacitanceBottom, CapacitanceCallibrated, BatteryLevel)'
        db_statement_string += ' VALUES '

        for sensor_reading in sensor_readings:
            db_row = {}
            ## map timestamp
            # if timestamp exists
            if 'timestamp' in sensor_reading.keys():
                print('ts found')            
                db_row['time'] = datetime.datetime.strptime(sensor_reading['timestamp'][:-1], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S.%f") # change format
            else:
                db_row['time'] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
                print('ts not found or too old')

            ## map tags
            db_row['device'] = sensor_reading['meta-data']['device']    # required field
            for k in ['location', 'method']:
                if k in sensor_reading['meta-data'].keys():
                    db_row[k] = "'" + sensor_reading['meta-data'][k] + "'"
                else:
                    db_row[k] = 'NULL'
            
            ## map measures
            for k in ['capacitance-full-length', 'capacitance-top', 'capacitance-bottom', 'capacitance-calibrated', 'battery']:
                if k in sensor_reading['measures'].keys():
                    db_row[k] = sensor_reading['measures'][k]
                else:
                    db_row[k] = 'NULL'

            db_statement_string += "('{0:s}', '{1:s}', {2:s}, {3:s}, {4}, {5}, {6}, {7}, {8}),".format(
                db_row['time'],
                db_row['device'],
                db_row['location'],
                db_row['method'],
                db_row['capacitance-full-length'],
                db_row['capacitance-top'],
                db_row['capacitance-bottom'],
                db_row['capacitance-calibrated'],
                db_row['battery']
            )
        
        db_statement_string = db_statement_string[:-1]  # trim last ','

        db_statement_strings.append(db_statement_string)

    return db_statement_strings


def main():
    # start
    print("Starting MQTT to SQL Forwarder...")
    # pause awhile while other containers startup
    time.sleep(50)

    # Initialize the MQTT client that should connect to the Mosquitto broker
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    print('MQTT username: ', MQTT_USERNAME)
    print('MQTT password: ', MQTT_PASSWORD)
    mqtt_client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    connOK=False
    while(connOK == False):
        try:
            mqtt_client.connect(MQTT_SERVER[0], MQTT_SERVER[1], 60)
            connOK = True
            print('Connected to MQTT server')
        except:
            connOK = False
        time.sleep(2)

    # Create a connection to the SQL database
    print('DB connection string: ', db_connection_string)
    connOK=False
    while(connOK == False):
        try:
            db_cnxn = pyodbc.connect(db_connection_string)
            connOK = True
            print('Connected to SQL Server')
        except:
            connOK = False
            print('.', end='')
        time.sleep(2)

    # Create a cursor from the connection
    db_cursor = db_cnxn.cursor()

    # TODO check db exists
    # TODO use db


    # Blocking loop to the Mosquitto broker
    # mqtt_client.loop_forever()
    mqtt_client.loop_start()

    while True:
        while len(incoming_queue) == 0:
            time.sleep(2)
        db_statement_strings = process_queue()

        ## encode and send to database
        print(db_statement_strings)
        for db_statement_string in db_statement_strings:
            # try:
            db_cursor.execute(db_statement_string)
            db_cnxn.commit()
            print("Wrote statment to SQL DB")
            # except:
                # print("** Error writing to SQL DB **")


if __name__ == '__main__':
    main()