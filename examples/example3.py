# -*- coding: utf-8 -*-
"""
This script shows the basic usage of the GIFSurface class.

When initializing a surface instance you must specify its
width and height. You also need to specify a palette for
this surface before you save it.
"""
import gifmaze as gm


width, height = 600, 400

surface = gm.GIFSurface(width, height, bg_color=0)
# you must specify at least one (r, g, b) color for this surface.
surface.set_palette('r')
surface.save('surface.gif')
surface.close()

surface = gm.GIFSurface.from_image('teacher.png')
surface.set_palette([0, 0, 0])
surface.save('teacher.gif')
surface.close()
