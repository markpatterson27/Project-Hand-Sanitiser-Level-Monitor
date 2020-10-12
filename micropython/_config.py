# config file. replace values below and rename file "config.py"

# check if const() defined
try:
    x = const(1)
except NameError:
    print("const not defined")
    const = lambda x: x

# WIFI_SSID = "<wifi ssid>"
# WIFI_PSK = "<wifi passphrase>"

ACCESS_POINTS = {
    "<wifi ssid>": "<wifi passphrase>"
}

MQTT_SERVERS = ("ip address:port", "ip address:port") # need to define more than one ip address

NTP_SERVER = "ip address or FQDN"

# pins ESP32
LED = const(5)
# SCL = const(22)
# SDA = const(21)
