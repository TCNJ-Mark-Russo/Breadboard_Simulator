# ssd1306.py
# SSD1306 component class proxies
# v. 0.2
# Mark F. Russo, PhD
# 4/27/2023

# References
# https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
# https://github.com/openmv/openmv/blob/master/scripts/libraries/ssd1306.py
# https://docs.micropython.org/en/latest/library/framebuf.html
# https://github.com/micropython/micropython/blob/master/extmod/modframebuf.c
# https://github.com/adafruit/micropython-adafruit-framebuf/blob/master/framebuf.py

# SSD1306_I2C OLED Proxy
import json, socket

port = 9999

# register definitions
SET_CONTRAST        = 0x81
SET_ENTIRE_ON       = 0xa4
SET_NORM_INV        = 0xa6
SET_DISP            = 0xae
SET_MEM_ADDR        = 0x20
SET_COL_ADDR        = 0x21
SET_PAGE_ADDR       = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP       = 0xa0
SET_MUX_RATIO       = 0xa8
SET_COM_OUT_DIR     = 0xc0
SET_DISP_OFFSET     = 0xd3
SET_COM_PIN_CFG     = 0xda
SET_DISP_CLK_DIV    = 0xd5
SET_PRECHARGE       = 0xd9
SET_VCOM_DESEL      = 0xdb
SET_CHARGE_PUMP     = 0x8d

class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        # Note the subclass must initialize self.framebuf to a framebuffer.
        # This is necessary because the underlying data buffer is different
        # between I2C and SPI implementations (I2C needs an extra byte).
        # self.poweron()
        # self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()
    
    def fill(self, val):
        # Fill OLED pixels with val (0 clears)
        msg = {'to':'oled', 'msg':'fill', 'val':val}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'fill' failed for OLED (SSD1306_I2C)")
        return True
    
    # Render text at pixel row, col with val
    def text(self, text, col, row, antialias=True):
        msg = {'to':'oled', 'msg':'text', 'col':col, 'row':row, 'text':text}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'text' failed for OLED (SSD1306_I2C)")
        return True
    
    # Draw the text on the OLED
    def show(self):
        msg = {'to':'oled', 'msg':'show'}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'show' failed for OLED (SSD1306_I2C)")
        return True

    # Render pixel at x, y with val
    def pixel(self, x, y, val):
        msg = {'to':'oled', 'msg':'pixel', 'x':x, 'y':y, 'val':val}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'pixel' failed for OLED (SSD1306_I2C)")
        return True

    # Render rectangle at x, y of size w, h with val
    def rect(self, x, y, w, h, val):
        msg = {'to':'oled', 'msg':'rect', 'x':x, 'y':y, 'width':w, 'height':w, 'val':val}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'rect' failed for OLED (SSD1306_I2C)")
        return True

    # Render filled rectangle at x, y of size w, h with val
    def fill_rect(self, x, y, w, h, val):
        msg = {'to':'oled', 'msg':'fill_rect', 'x':x, 'y':y, 'width':w, 'height':w, 'val':val}
        resp = self._send(msg)
        if not resp['success']:
            raise RuntimeError(f"Command 'fill_rect' failed for OLED (SSD1306_I2C)")
        return True
    
    def scroll(self, dx, dy):
        # self.framebuf.scroll(dx, dy)
        pass

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))
        
    # Helper
    def _send(self, msg):
        bytes = json.dumps(msg).encode('utf-8')         # Serialize and encode as bytes
        self.sock.sendto(bytes, ('127.0.0.1', port))    # Send message to board simulator
        bytes, addr = self.sock.recvfrom(1024)          # Wait for response
        return json.loads(bytes.decode())               # Decode and return

# SSD1306_I2C Proxy
class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c  = i2c
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)
        
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 0))    # Bind to localhost at arbitrary available port.

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        # self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.temp[0] = self.addr << 1
        self.temp[1] = 0x40 # Co=0, D/C#=1
        # self.i2c.start()
        # self.i2c.write(self.temp)
        # self.i2c.write(buf)
        # self.i2c.stop()
