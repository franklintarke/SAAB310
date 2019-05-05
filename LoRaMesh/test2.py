from network import LoRa
import socket
import time
import utime
import ubinascii
import pycom
import machine
from network import WLAN
import machine
import usocket

pycom.wifi_on_boot(True)

f = 'hello'
a = f.encode('utf-8')
a.decode()


try:
    import urequests as requests
except ImportError:
    import requests

r = requests.get('http://192.168.4.2:3000/')
print(r)
print(r.content)
print(r.text)
print(r.content)
print(r.json())

# It's mandatory to close response objects as soon as you finished
# working with them. On MicroPython platforms without full-fledged
# OS, not doing so may lead to resource leaks and malfunction.
r.close()
