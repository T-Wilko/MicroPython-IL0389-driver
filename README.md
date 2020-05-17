# MicroPython-IL0389-driver
IL0389 EPD IC Driver - Parameters are currently set for a 400x300 BW screen

## Usage with epaper.py (i.e. code to be used in main.py)
#### Displays a test frame of text, rectangles, and lines

```
import epaper, framebuf

width = 400
height = 300

e = epaper.EPD()
e.init()
e.clearBuffer()

# Create a buffer object for framebuf to interact with
buf = bytearray(width*height // 8) 

# Create a framebuf object with monochrome HLSB mapping
fb = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB) 

black = 1
white = 0

# Set what you want your background (primary) and secondary colours to be
primary, secondary = white, black

# Draw the test frame
fb.fill(primary)
fb.text('Hello World - 123456789', 15, height//3, secondary)
fb.fill_rect(width//20, 2*(height//3), 30, 30, secondary)
fb.rect(width//20, 2*(height//3)+40, 30, 30, secondary)
fb.vline(width//20 + 50, 2*(height//3), 70, secondary)
for i in range(8):
    fb.hline(width//20 + 60, 2*(height//3)+(10*i), 50, secondary)

# Display the image
e.displayBuffer(buf)

```

## Usage with epaper_framebuf.py (i.e. code to be used in main.py)
#### Displays a test frame of text, rectangles, and lines

```
import epaper_framebuf as EFB

width = 400
height = 300

# Create a framebuf object that doubles as an epaper interaction object
efb = EFB.EPD(width, height)

black = 1
white = 0

# Set what you want your background (primary) and secondary colours to be
primary, secondary = white, black

# Draw the test frame
efb.fill(primary)
efb.text('Hello World - 123456789', 15, height//3, secondary)
efb.fill_rect(width//20, 2*(height//3), 30, 30, secondary)
efb.rect(width//20, 2*(height//3)+40, 30, 30, secondary)
efb.vline(width//20 + 50, 2*(height//3), 70, secondary)
for i in range(8):
    efb.hline(width//20 + 60, 2*(height//3)+(10*i), 50, secondary)

# Display the image
efb.show()

```

## Features coming soon
 - Variable width and height through parameter input during object initialisation
 - 4 tone grayscale implementation
 - Partial refresh / no-flicker refresh

