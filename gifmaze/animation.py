# -*- coding: utf-8 -*-
"""
`Animation` is the middle layer object that controls how
a `Maze` object is rendered to a `GIFSurface` object.
"""
from functools import partial
from . import encoder


class Render(object):
    """
    This class encodes the region specified by the `frame_box` attribute of a maze
    into one frame in the GIF image.
    """
    def __init__(self, cmap, mcl):
        """
        cmap: a dict that maps the value of the cells to their color indices.

        mcl: the minimum code length for the LZW compression.

        A default dict is initialized so that one can set the colormap by
        just specifying what needs to be specified.
        """
        self.colormap = {i: i for i in range(1 << mcl)}
        if cmap:
            self.colormap.update(cmap)
        self.compress = partial(encoder.lzw_compress, mcl=mcl)

    def __call__(self, maze):
        """
        Encode current maze into one frame and return the encoded data.
        Note the graphics control block is not added here.
        """
        # the image descriptor
        if maze.frame_box is not None:
            left, top, right, bottom = maze.frame_box
        else:
            left, top, right, bottom = 0, 0, maze.width - 1, maze.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = encoder.image_descriptor(maze.scaling * left + maze.translation[0],
                                              maze.scaling * top  + maze.translation[1],
                                              maze.scaling * width,
                                              maze.scaling * height)

        # A generator that yields the pixels of this frame. This may look a bit unintuitive
        # because encoding frames will be called thousands of times in an animation and
        # we should avoid creating and destroying a new list each time it's called.
        def get_frame_pixels():
            for i in range(width * height * maze.scaling * maze.scaling):
                y = i // (width * maze.scaling * maze.scaling)
                x = (i % (width * maze.scaling)) // maze.scaling
                val = maze.get_cell((x + left, y + top))
                yield self.colormap[val]

        # the compressed image data of this frame
        data = self.compress(get_frame_pixels())
        # clear `num_changes` and `frame_box`
        maze.reset()

        return descriptor + data


class Animation(object):
    """
    This class is the main entrance for calling algorithms to
    run and rendering the maze into the image.
    """

    def __init__(self, surface):
        self._gif_surface = surface

    def pause(self, delay, trans_index=0):
        """Pause the animation by padding a 1x1 invisible frame."""
        self._gif_surface.write(encoder.pause(delay, trans_index))

    def paint(self, *args):
        """Paint a rectangular region in the surface."""
        self._gif_surface.write(encoder.rectangle(*args))

    def run(self, algo, maze, delay=5, trans_index=None,
            cmap=None, mcl=8, **kwargs):
        """
        The entrance for running the animations.

        --------
        Parameters:


        algo: name of the algorithm.

        maze: an instance of the `Maze` class.

        delay: delay time between successive frames.

        trans_index: the transparent channel.
            `None` means there is no transparent color.

        cmap: a dict that maps the values of the cells in a maze
            to their color indices.

        mcl: see the doc for the lzw_compress.
        """
        render = Render(cmap, mcl)
        control = encoder.graphics_control_block(delay, trans_index)
        for frame in algo(maze, render, **kwargs):
            self._gif_surface.write(control + frame)
