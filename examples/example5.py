# -*- coding: utf-8 -*-
"""
This script shows how to use a mask image in a maze.
"""
import gifmaze as gm
from gifmaze.algorithms import kruskal


width, height = 605, 405
surface = gm.GIFSurface(width, height, bg_color=0)
surface.set_palette([0, 0, 0, 255, 255, 255])
anim = gm.Animation(surface)

mask = gm.generate_text_mask((width, height), 'UST', 'ubuntu.ttf', 300)
maze = gm.Maze(119, 79, mask=mask).scale(5).translate((5, 5))

anim.pause(200)
anim.run(kruskal, maze, speed=30, delay=5, trans_index=None,
         mcl=2, cmap={0: 0, 1: 1})
anim.pause(500)

surface.save('example5_anim_with_mask.gif')
surface.close()
