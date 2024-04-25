# lsm6dsox.py
# LMS6SOX IMU component class proxies
# v. 0.3
# Author: Mark F. Russo, PhD
# Copyright (c) 2023-2024 

# References
# https://github.com/openmv/openmv/blob/master/scripts/libraries/lsm6dsox.py

import json, socket, random

port = 9999

# LSM6DSOX Proxy
class LSM6DSOX:
    _DEFAULT_ADDR = 0x6A
    
    def __init__(self, bus, 
               cs_pin=None, address=_DEFAULT_ADDR, gyro_odr=104, accel_odr=104, 
               gyro_scale=2000, accel_scale=4, ucf=None):
        self.bus     = bus
        self.address = address
        
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 0))    # Bind to localhost at arbitrary available port.

    def reset(self):
        pass
    
    def set_mem_bank(self, bank):
        pass
    
    def set_embedded_functions(self, enable, emb_ab=None):
        pass

    def load_mlc(self, ucf):
        pass
    
    def read_mlc_output(self):
        pass
    
    def gyro(self):
        return self.read_gyro()
    
    def read_gyro(self):
        """Returns gyroscope vector in degrees/sec."""
        msg = {'to':'lsm6dsox', 'msg':'read_gyro'}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'read_gyro' failed for LSM6DSOX")
        return resp['msg']
    
    def accel(self):
        return self.read_accel()
    
    def read_accel(self):
        """Returns acceleration vector in gravity units (9.81m/s^2)."""
        msg = {'to':'lsm6dsox', 'msg':'read_accel'}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'read_accel' failed for LSM6DSOX")
        return resp['msg']
    
    # Helper
    def _send(self, msg):
        bytes = json.dumps(msg).encode('utf-8')         # Serialize and encode as bytes
        self.sock.sendto(bytes, ('127.0.0.1', port))    # Send message to board simulator
        bytes, addr = self.sock.recvfrom(1024)          # Wait for response
        return json.loads(bytes.decode())               # Decode and return
