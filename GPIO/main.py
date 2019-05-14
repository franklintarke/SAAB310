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
timer = Timer.Alarm(None, 1.5, periodic = False)

btn = Pin('P21', mode=Pin.IN, pull=Pin.PULL_UP)

def long(count):
   print('Long Press',count)

def short(count):
   print('Short Press',count)

count = 0
butms = 0
val = 0
def btn_press_detected(arg):
  global butms, count
  now = time.ticks_ms()
  if butms == 0: butms = now
  else:
    if butms == now: return
  i = 0
  while i < 10:
    time.sleep_ms(1)
    if pin() == 1: i = 0
    else: i+=1
  while pin() == 0:
    i+=1
    if(i > 1000): break
    time.sleep_ms(1)

    if(i>1000):
        long(count)
    else:
        short(count)
    arg = 1

    return val = arg


btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,  btn_press_detected, val)
