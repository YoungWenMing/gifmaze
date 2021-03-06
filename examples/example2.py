# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Tutorial on the GIF89a Specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This script generates a GIF image that contains three frames.
The delay of each frame is 1 second.

The structure of the GIF file is as follows:

1. Firstly the screen descriptor which specifies the size of
    the image as well as the global color table.

2. Then the global color table.

3. Then the loop control block.

4. Then the data of the three frames. Each frame is further divided into:
    (i) its graphics control block.
    (ii). its image descriptor.
    (iii). its LZW compressed pixel data.

5. Finally the trailor `0X3B`.
"""
from gifmaze import encoder

# size of the image.
width, height = 300, 300

# the palette contains 4 colors.
color_depth = 2

# 1. the logical screen descriptor.
screen = encoder.screen_descriptor(width, height, color_depth)

# 2. the global color table.
palette = bytearray([255, 0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0])

# 3. the loop control block.
loop_control = encoder.loop_control_block(0)

# 4-1. the graphics control block (delay, transpaernt)
graphics_control = encoder.graphics_control_block(100, None)

# 4-2. the image descriptor.
descriptor = encoder.image_descriptor(0, 0, width, height)

# 4-3. the compressed data of each frame.
frames = []
for i in range(3):
    compressed_data = encoder.lzw_compress([i] * width * height, mcl=2)
    frames.append(compressed_data)

# 5. the trailor '0x3B'.
trailor = bytearray([0x3B])

# put them together.

data = bytearray()
for frame in frames:
    data += graphics_control + descriptor + frame

with open('example2_loop.gif', 'wb') as f:
    f.write(screen
            + palette
            + loop_control
            + data
            + trailor)
