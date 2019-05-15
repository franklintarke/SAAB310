from machine import *
import time
from machine import Timer
from machine import Pin
import gc

# initialize `P9` in gpio mode and make it an output
#p_out = Pin('P9', mode=Pin.OUT)
from machine import Pin, PWM
from time import sleep

frequency = 5000
led_GREEN = PWM(0, frequency)
led_GREEN.channel(0,pin='P9', duty_cycle=.1)

led_BLUE = PWM(0, frequency)
led_BLUE.channel(1,pin='P10', duty_cycle=0)

led_RED = PWM(0, frequency)
led_RED.channel(2,pin='P11', duty_cycle=1)



chrono = Timer.Chrono()
timer = Timer.Alarm(None, .2, periodic = False)
timer2 = Timer.Alarm(None, 3, periodic = False)

btn = Pin('P21', mode=  Pin.IN, pull=Pin.PULL_UP)

def long_press_handler(alarm):
    print("****** LONG PRESS HANDLER ******")

def single_press_handler():
    print("****** BUTTON PRESSED ******")

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

btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,  btn_press_detected)
