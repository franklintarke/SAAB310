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
py = Pytrack()
l76 = L76GNSS(py, timeout=30)

rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')
sd = SD()
os.mount(sd, '/sd')
os.listdir('/sd')

while (True):
    coord = l76.coordinates()
    f = open('/sd/gps-record.txt', 'w')
    f.write("{} - {}\n".format(coord, rtc.now()))
    print("{}".format(coord))
    time.sleep(10)
