# time2.py
from time import sleep, time

# Replace timer methods from micropython
def sleep_ms(ms): sleep(ms/1000)
def ticks_ms():   return int(time()*1000)
