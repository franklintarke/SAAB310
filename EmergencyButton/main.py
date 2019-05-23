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


#**********BUTTON DETECTION**************

chrono = Timer.Chrono()
timer = Timer.Alarm(None, 3, periodic = False)
timer2 = Timer.Alarm(None, .2, periodic = False)
btn = Pin('P22', mode=  Pin.IN, pull=Pin.PULL_UP)
emergencymode = 0;

def long_press_handler(alarm):
    #EMERGENCY BUTTON
    global emergencymode
    fastBlinkLED()
    coord = getGPS()
    print("****** EMERGENCY BUTTON ******")
    if emergencymode == 0:
        emergencymode = 1
    else:
        emergencymode =0

        for x in range(1):
            led_GREEN.channel(0,pin='P20', duty_cycle=.8)
            time.sleep_ms(1000)
            led_GREEN.channel(0,pin='P20', duty_cycle=0)
            time.sleep_ms(100)

    print(emergencymode)
    print(coord)

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
        #else:
            #timer.callback(None)
            #chrono.stop()
            #t = chrono.read_ms()
            #if (t > 30) & (t < 200):
                #pass
                #single_press_handler()
    finally:
        gc.collect()

btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,  btn_press_detected)


#******************GPS CODE*********************
#GPS
def getGPS():
    py = Pytrack()
    l76 = L76GNSS(py, timeout=30)
    coord = l76.coordinates()
    #print(coord)
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
led_GREEN = PWM(0, frequency)

def fastBlinkLED():
    for x in range(10):
        led_RED.channel(2,pin='P19', duty_cycle=1)
        time.sleep_ms(100)
        led_RED.channel(2,pin='P19', duty_cycle=0)
        time.sleep_ms(100)
