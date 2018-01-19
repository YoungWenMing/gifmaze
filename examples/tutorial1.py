# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Tutorial on the GIF89a Specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This script generates a single static gif image of red color.
It contains:

1. Firstly the screen descriptor which specifies the size of
    the image as well as the global color table.

2. Then the global color table.

3. Then the static frame. This frame is further divided into:
    (i). its image descriptor.
    (ii). its LZW compressed pixel data.

4. Finally the trailor `0X3B`.

The loop control block and graphics control block are not needed.
"""
from gifmaze import Compression, GIFEncoder

# size of the image.
width, height = 100, 100

# set the size of the global color table,
# `1` means there are two colors in the global color table.
color_depth = 1

# 1. the logical screen descriptor.
screen = GIFEncoder.screen_descriptor(width, height, color_depth)

# 2. the global color table, here it contains two colors: red and black.
palette = bytearray([255, 0, 0, 0, 0, 0])

# 3-1. the image descriptor of the frame.
descriptor = GIFEncoder.image_descriptor(0, 0, width, height)

# 3-2. the LZW compressed pixel data.
data = Compression(2)([0] * width * height)

# 4. the trailor '0x3B'.
trailor = bytearray([0x3B])

# put them together.
with open('tutorial1.gif', 'wb') as f:
    f.write(screen
            + palette
            + descriptor
            + data
            + trailor)
