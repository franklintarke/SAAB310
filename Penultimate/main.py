from network import Bluetooth
from network import LoRa
import socket
import time
import utime
import ubinascii
import pycom
import machine
try:
    import urequests as requests
except ImportError:
    import requests
from loramesh import Loramesh



from machine import *
import time
from machine import Timer
from machine import Pin
import gc
from machine import Pin, PWM
from time import sleep
import math
import network
import os
import utime
from L76GNSS import L76GNSS
from pytrack import Pytrack

#*******SETUP CODE****************
pycom.wifi_on_boot(False)
pycom.heartbeat(False)
pycom.rgbled(0x000000)

lora = LoRa(mode=LoRa.LORA, region=LoRa.US915, bandwidth=LoRa.BW_125KHZ, sf=7)
MAC = str(ubinascii.hexlify(lora.mac()))[2:-1]
print("LoRa MAC: %s"%MAC)
mesh = Loramesh(lora)
DevIP = mesh.ipaddr()[-2]
print(DevIP)


#########BLUETOOTH CODE#############

bluetooth = Bluetooth()
bluetooth.set_advertisement(name='LoPy', service_uuid=b'SAABlopy12345678')

def conn_cb (bt_o):
    events = bt_o.events()
    if  events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected")
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print("Client disconnected")

bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)

bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=b'SAABlopy12345678', isprimary=True)

chr1 = srv1.characteristic(uuid=b'ab34567890123456', value=5)

char1_read_counter = 0
def char1_cb_handler(chr):
    global char1_read_counter
    char1_read_counter += 1

    events = chr.events()
    if  events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request with value = {}".format(chr.value()))
        #Call method to do GET Request
        if chr.value().decode("utf-8") == 'GET':
            makeGETRequest()
        if chr.value().decode("utf-8") == 'POST':
            makePOSTRequest()


    if events & Bluetooth.CHAR_READ_EVENT:
        global packageList
        data = str(packageList)
        packageList = []
        return data

char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)

srv2 = bluetooth.service(uuid=1234, isprimary=True)


#****************GET REQUEST CODE*****************
# create UDP socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
myport = 1234
s.bind(myport)

hubAddresses = ['fdde:ad00:beef:0:9148:2412:984:42a1','fdde:ad00:beef:0:6834:9acd:e673:b95c']
everyone = 'ff03::1'

hubCounter =0

def makeGETRequest():
    global hubCounter
    if hubCounter >= 2:
        hubCounter = 0
    try:
        s.sendto('makeGETrequest', (everyone, myport))   #hubAddresses[hubCounter]
        print('Sent GET request')
        print(hubAddresses[hubCounter])
        hubCounter = hubCounter + 1;
    except Exception:
        pass
        print('failedtosend')
    time.sleep(5)

def makePOSTRequest(data):
    global hubCounter
    if hubCounter >= 2:
        hubCounter = 0
    try:
        s.sendto('makePOSTrequest', (everyone, myport))   #hubAddresses[hubCounter]
        print('Sent POST request')
        print(hubAddresses[hubCounter])
        hubCounter = hubCounter + 1;
    except Exception:
        pass
        print('failedtosend')
    time.sleep(5)

#*************RECEIVE MESSAGE HANDLER****************
packageList = []
def receive_pack():
    # listen for incomming packets
    global packageList
    while True:
        rcv_data, rcv_addr = s.recvfrom(128)
        if len(rcv_data) == 0:
            break
        rcv_ip = rcv_addr[0]
        rcv_port = rcv_addr[1]
        print('Incomming %d bytes from %s (port %d)'%(len(rcv_data), rcv_ip, rcv_port))
        print(rcv_data)
        packageList.append(rcv_data)
        # could send some ACK pack:
        if rcv_data.startswith("Hello"):
            try:
                s.sendto('ACK ' + MAC + ' ' + str(rcv_data)[2:-1], (rcv_ip, rcv_port))
            except Exception:
                pass

        mesh.blink(7, .3)

ip = mesh.ip()
mesh.mesh.rx_cb(receive_pack)


#*******************EMERGENCY BUTTON CODE******************

#**********BUTTON DETECTION**************

chrono = Timer.Chrono()
timer = Timer.Alarm(None, 3, periodic = False)
timer2 = Timer.Alarm(None, .2, periodic = False)
btn = Pin('P21', mode=  Pin.IN, pull=Pin.PULL_UP)
emergencymode = 0;

def long_press_handler(alarm):
    #EMERGENCY BUTTON
    global emergencymode
    fastBlinkLED()

    print("****** EMERGENCY BUTTON ******")
    if emergencymode == 0:
        emergencymode = 1
        #gpsCoords = getGPS()
        try:
            s.sendto('emergency' + str(coords), (everyone, myport))   #hubAddresses[hubCounter]
            print('Sent EMERGENCY beacon')
            print('hubct' + str(hubAddresses[hubCounter]))
            hubCounter = hubCounter + 1;
        except Exception:
            pass
            print('failedtosend EMERGENCY')
        time.sleep(5)
    else:
        emergencymode =0
    print(emergencymode)

def single_press_handler(alarm):
    #CHECK POWER
    #getBatteryCharge()
    print("****** CHECK POWER ******")

def btn_press_detected(arg):
    global chrono,  timer, timer2
    try:
        val = btn()
        if 0 == val:
            chrono.reset()
            chrono.start()
            timer.callback(long_press_handler)
            timer2.callback(single_press_handler)
        else:
            timer.callback(None)
            chrono.stop()
            t = chrono.read_ms()
            if (t > 30) & (t < 200):
                pass
                #single_press_handler()
    finally:
        gc.collect()

#btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,  btn_press_detected)


#******************GPS CODE*********************
#GPS
def getGPS():
    py = Pytrack()
    l76 = L76GNSS(py, timeout=30)
    coord = l76.coordinates()
    print(coord)
    return coord


#*****************GET BATTERY POWER ************

def getBatteryCharge():
    py = Pytrack()
    py.read_battery_voltage()
    print(py.read_battery_voltage())

#****************Get Current Time***************
#Needs adjustment, RTC not avialable without internet
def getTime():
    rtc = RTC()
    rtc.ntp_sync("pool.ntp.org")
    utime.sleep_ms(750)
    print('\nRTC Set from NTP to UTC:', rtc.now())
    utime.timezone(7200)
    print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

#****************BlinkLED**********
frequency = 5000
led_RED = PWM(0, frequency)
def fastBlinkLED():
    for x in range(10):
        led_RED.channel(2,pin='P11', duty_cycle=1)
        time.sleep_ms(100)
        led_RED.channel(2,pin='P11', duty_cycle=0)
        time.sleep_ms(100)
