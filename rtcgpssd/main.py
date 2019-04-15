import machine
import math
import network
import os
import time
import utime
import gc
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from pytrack import Pytrack

time.sleep(2)
gc.enable()
#GPS
py = Pytrack()
l76 = L76GNSS(py, timeout=30)
#Real Time Clock
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')
#SD Card
sd = SD()
os.mount(sd, '/sd')
os.listdir('/sd')
f = open('/sd/gps-record.txt', 'w')

while (True):
    #l76.coordinates() retrieves its gps location in GNSS format
    coord = l76.coordinates()
    f.write("{} - {}\n".format(coord, rtc.now()))
    print("{}".format(coord))
    time.sleep(10)
