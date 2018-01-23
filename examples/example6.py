# -*- coding: utf-8 -*-
"""
This script combines two algorithms together in one animation.
It has full 256 colors in the global color table.
"""
from colorsys import hls_to_rgb
import gifmaze as gm
from gifmaze.algorithms import random_dfs, bfs


width, height = 605, 405
surface = gm.GIFSurface(width, height, bg_color=0)

palette = [0, 0, 0, 255, 255, 255, 255, 0, 255]
for i in range(256):
    rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    palette += [int(round(255 * x)) for x in rgb]

surface.set_palette(palette)

anim = gm.Animation(surface)
mask = gm.generate_text_mask((width, height), 'UST', 'ubuntu.ttf', 300)
maze = gm.Maze(119, 79, mask=mask).scale(5).translate((5, 5))

# pause two seconds, get ready!
anim.pause(200)

# run the maze generation algorithm.
anim.run(random_dfs, maze, speed=15, delay=5, mcl=2,
         cmap={0: 0, 1: 1, 2: 2, 3: 3}, trans_index=None, start=(0, 0))

# pause three seconds to see the result clearly.
anim.pause(300)
surface.save('tutorial6-1.gif')

# run the maze solving algorithm.
# the tree and wall are unchanged throughout the maze solving algorithm hence
# it's safe to use 0 as the transparent color.
# In the bfs algorithm the cells are marked by their distance to the starting cell,
# so we must define our color map dict first.
# The idea is to map the values of the cells into range 0-255.
cmap = {i: max(i % 256, 3) for i in range(len(maze.cells))}
cmap.update({0: 0, 1: 0, 2: 2})
anim.run(bfs, maze, speed=30, delay=5, mcl=8, cmap=cmap,
         trans_index=0, start=(0, 0), end=(maze.width - 1, maze.height - 1))

# pause five seconds to see the path clearly.
anim.pause(500)

# save the result.
surface.save('tutorial6-2.gif')
surface.close()
