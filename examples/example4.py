# -*- coding: utf-8 -*-
"""
This script shows how to run an animation on a maze.
"""
import gifmaze as gm
from gifmaze.algorithms import prim


# size of the image.
width, height = 605, 405

# 1. define a surface to draw on.
surface = gm.GIFSurface(width, height, bg_color=0)

# define the colors of the walls and tree.
# we use black for walls and white for the tree.
surface.set_palette('kw')

# 2. define an animation environment to run the algorithm.
anim = gm.Animation(surface)

# 3. add a maze into the scene.
# the size of the maze is 119x79 but it's scaled by 5
# (so it occupies 595x395 pixels) and is translated 5 pixels
# to the right and 5 pixels to the bottom to make it located
# at the center of the image.
maze = gm.Maze(119, 79, mask=None).scale(5).translate((5, 5))

# pause two seconds, get ready!
anim.pause(200)

# 4. the animation runs here.
# `speed` controls the speed of the animation,
# `delay` controls the delay between successive frames,
# `trans_index` is the transparent color index,
# `mcl` is the minimum code length for encoding the animation
# into frames, it's at least 2 and must satisfy
# 2**mcl >= number of colors in the global color table.
# `start` is the starting cell for running Prim's algorithm. (it's a cell,
# not a pixel).
# `cmap` controls how the cells are mapped to colors, i.e. {cell: color}.
# here `cmap={0: 0, 1: 1}` means the cells have value 0 (the walls) are colored
# with the 0-indexed color (black), cells have value 1 (the tree) are colored
# with the 1-indexed color (white).
anim.run(prim, maze, speed=30, delay=5, trans_index=None,
         cmap={0: 0, 1: 1}, mcl=2, start=(0, 0))

# pause five seconds to see the result clearly.
anim.pause(500)

# 5. save the result.
surface.save('example4_simple_anim.gif')
surface.close()
