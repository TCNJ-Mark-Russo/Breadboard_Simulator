# machine.py
# Machine module simulator and component class proxies
# v. 0.1
# Mark F. Russo, PhD
# 1/6/2023

import socket, json, random

# IP address on which board simulator is listening for UDP datagram packets
ADDR = '127.0.0.1'

# Board simulator port'
PORT = 9999

# Pin Proxy
# https://docs.micropython.org/en/latest/library/machine.Pin.html
class Pin:
    # Mode
    IN  = 0
    OUT = 1
    ALT = 2
    ANALOG = 3
    OPEN_DRAIN = 5
    ALT_OPEN_DRAIN = 6
    
    # Resistor
    PULL_NONE = None
    PULL_UP   = 1
    PULL_DOWN = 2
    PULL_HOLD = 3
    
    def __init__(self, id, mode=OUT, pull=False, value=None, drive=0, alt=- 1):
        self.id     = id
        self.mode   = mode
        self.pull   = pull
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ADDR, 0))    # Bind to localhost at arbitrary available port.

    # Turn pin on
    def on(self):
        msg = {'to':'pin', 'num':self.id, 'msg':'on'}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'on' failed for Pin {self.id}")
        return True

    # Turn pin off
    def off(self):
        msg = {'to':'pin', 'num':self.id, 'msg':'off'}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'off' failed for Pin {self.id}")
        return True
    
    # Query and return pin value
    def value(self):
        msg = {'to':'pin', 'num':self.id, 'msg':'value'}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'value' failed for Pin {self.id}")
        try:
            return int(resp['msg'])
        except Exception as e:
            raise
    
    # Utility function to send a message dictionary and return a response
    def _send(self, msg):
        bytes = json.dumps(msg).encode('utf-8')         # Serialize and encode as bytes
        self.sock.sendto(bytes, (ADDR, PORT))           # Send message to board simulator
        bytes, addr = self.sock.recvfrom(1024)          # Wait for response
        return json.loads(bytes.decode())               # Decode and return

# I2C serial bus Object Proxy
# https://docs.micropython.org/en/latest/library/machine.I2C.html
class I2C:
    def __init__(self, chan, scl=Pin(13), sda=Pin(12), freq=400_000):
        self.chan = chan
        self.scl  = scl
        self.sda  = sda
        self.freq = freq

# ADC Proxy
# https://docs.micropython.org/en/latest/library/machine.ADC.html
class ADC:
    def __init__(self, pin):
        self.pin = pin
        
    def read_u16(self):
        # read value, 0-65535 across voltage range 0.0v - 3.3v
        return random.randrange(0, 65536)

# PWM Proxy
# https://docs.micropython.org/en/latest/library/machine.PWM.html
class PWM:
    def __init__(self, pin):
        self.pin = pin
        self._freq = 1000
        self._duty = 200

    def freq(self, val=None):
        # If no val return freq
        if not self._freq:
            return self._freq
        else:
            self._freq = val
    
    def duty_u16(self, val=None):
        # If no val return duty cycle
        if not self._duty:
            return self._duty
        else:
            self._duty = val
    
    def deinit(self):
        # turn off PWM on the pin
        pass