'''
IL0389 EPD IC Framebuf-derived Driver - Parameters are for a 400x300 BW screen

Written by Thomas Wilkinson - github.com/T-Wilko

'''

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
import ustruct, framebuf

## Display command addresses
PANEL_SETTING                       = const(0x00)
POWER_SETTING                       = const(0x01)
POWER_OFF                           = const(0x02)
POWER_OFF_SEQ_SET                   = const(0x03)
POWER_ON                            = const(0x04)
POWER_ON_MEASURE                    = const(0x05)
BOOSTER_SOFT_START_CONTROL          = const(0x06)
DEEP_SLEEP_MODE                     = const(0x07)
START_TRANSMISSION_1                = const(0x10)
DATA_STOP                           = const(0x11)
DISP_REFRESH                        = const(0x12)
START_TRANSMISSION_2                = const(0x13)
PLL_CONTROL                         = const(0x30)
TEMP_CALIBRATION                    = const(0x40)
TEMP_SENSOR_SELECTION               = const(0x41)
TEMP_SENSOR_WRITE                   = const(0x42)
TEMP_SENSOR_READ                    = const(0x43)
VCOM_DATA_INT_SETTING               = const(0x50)
LOW_POWER_DETECT                    = const(0x51)
TCON_SETTING                        = const(0x60)
RES_SETTING                         = const(0x61)
GSST_SETTING                        = const(0x65)
REVISION                            = const(0x70)
GET_STATUS                          = const(0x71)
AUTO_MEASURE_VCOM                   = const(0x80)
VCOM_READ                           = const(0x81)
VCM_DC_SETTING                      = const(0x82)
#PARTIAL_WINDOW                     = const(0x90)
PARTIAL_IN                          = const(0x91)
PARTIAL_OUT                         = const(0x92)
PROGRAM_MODE                        = const(0xA0)
ACTIVE_PROG                         = const(0xA1)
READ_OTP                            = const(0xA2)
CASCADE_SETTING                     = const(0xE0)
POWER_SAVING                        = const(0xE3)
FORCE_TEMP                          = const(0xE5)

class EPD(framebuf.FrameBuffer):
    def __init__(self, width, height):
        
        self.spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
        #self.spi = SPI(1, 10000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self.spi.init()
        dc = Pin(27)
        cs = Pin(5)
        rst = Pin(14)
        busy = Pin(4)
        
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = width
        self.height = height
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()
    
    def init_display(self):
        #Reset EPD Driver IC
        self.reset()
        
        #Booster soft start
        self._command(BOOSTER_SOFT_START_CONTROL, b'\x17\x17\x17')
        
        #Power setting
        self._command(POWER_SETTING, b'\x03\x00\x2B\x2B\x09')
        
        #Power on
        self._command(POWER_ON)
        
        #Check busy pin and proceed if idle
        self.wait_until_idle()
        
        #Panel setting - B&W and full resolution
        self._command(PANEL_SETTING, b'\x1F')
        
        #PLL control - Set to 100Hz, default is 50Hz
        self._command(PLL_CONTROL, b'\x3A')
        
        #Resolution setting
        self._command(RES_SETTING, b'\x01\x90\x01\x2C')
        
        #VCM_DC setting - Currently set to -1V, default is -0.1V i.e. b'\x00'
        self._command(VCM_DC_SETTING, b'\x12')
        
        #VCOM and Data Interval setting
        self._command(VCOM_DATA_INT_SETTING, b'\x87')
        
        #Finish initialisation with refresh of a blank screen
        self.fill(0)
        self.show()
        
    def poweroff(self):
        self._command(POWER_OFF)
        
    def poweron(self):
        self._command(POWER_ON)
    
    def show(self):
        self._command(START_TRANSMISSION_2)
        self._data(self.buffer)
        self._command(DATA_STOP)
        self._command(DISP_REFRESH)
        self.wait_until_idle()    
    
    # To display your own buffer, instead of the framebuf buffer
    def show_buffer(self, buf):
        self.wait_until_idle()
        self._command(START_TRANSMISSION_2)
        for i in range(0, len(buf)):
            self._data(bytearray([buf[i]]))
        self._command(DATA_STOP)
        self._command(DISP_REFRESH)
        self.wait_until_idle()
        
    def _command(self, command, data=None):
        self.cs(1) # according to LOLIN_EPD
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.cs(1) # according to LOLIN_EPD
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)
        
    def wait_until_idle(self):
        while self.busy == 0:
            pass
        return

    def reset(self):
        self.rst(1)
        sleep_ms(1)

        self.rst(0)
        sleep_ms(10)

        self.rst(1)

    # to wake call reset() or init()
    def sleep(self):
        self._command(bytearray([DEEP_SLEEP_MODE]))
        self.wait_until_idle()
