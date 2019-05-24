from time import sleep_ms, ticks_ms
from machine import Pin
import gc

class BUTTON:

  def __init__(self,pid='P4',longms=1000):
    self.longms = longms
    self.butms = 0
    self.pin = Pin(pid, mode=Pin.IN, pull=Pin.PULL_UP)
    self.pin.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,  self.press)

  def long(self):
    pass

  def short(self):
    pass

  def press(self,pin):
    now = ticks_ms()
    if self.butms == 0: self.butms = now
    else:
      if self.butms == now: return
    i = 0
    while i < 10:
      sleep_ms(1)
      if self.pin() == 1: i = 0
      else: i+=1

    while self.pin() == 0:
      i+=1
      if(i > self.longms): break
      sleep_ms(1)

    if(i>1000): self.long()
    else: self.short()
    while self.pin() == 0: pass
    gc.collect()
