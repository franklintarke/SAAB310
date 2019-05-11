from machine import *

# initialize `P9` in gpio mode and make it an output
#p_out = Pin('P9', mode=Pin.OUT)
from machine import Pin, PWM
from time import sleep

frequency = 5000
led_GREEN = PWM(0, frequency)
led_GREEN.channel(0,pin='P9', duty_cycle=0.1)

led_BLUE = PWM(0, frequency)
led_BLUE.channel(1,pin='P10', duty_cycle=0)

led_RED = PWM(0, frequency)
led_RED.channel(2,pin='P11', duty_cycle=1)

def buttonPress(arg):
    print('BUTTON DEPRESSED!')

button = Pin('P21', mode=Pin.IN, pull=Pin.PULL_UP)
#while True:
    #if button() == 0:
        #print('Button pressed!'


button.callback(Pin.IRQ_LOW_LEVEL, buttonPress,arg = None)
