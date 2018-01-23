<p align="left"><img src="logo.svg" width="400"/></p>

# GIFMaze

[![PyPI version](https://badge.fury.io/py/gifmaze.svg)](https://badge.fury.io/py/gifmaze) [![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT) [![PyPI](https://img.shields.io/pypi/pyversions/pytest.svg)]()


## What's cool

The following image illustrates two graph algorithms: it firstly used Wilson's algorithm to generate an uniform spanning tree of the 2-D grid (the result is a perfectly random sampled maze) and then used breadth first search to solve this maze. It contains roughly 1520 frames, but the file size is only 670KB! 

<p align="center"><img src="https://neozhaoliang.github.io/img/gifmaze/wilson-bfs.gif"></p>


## Installation

You can install either via pip:

```bash
pip install gifmaze
```
or via git

```bash
git clone https://github.com/neozhaoliang/gifmaze gifmaze && cd gifmaze && python setup.py install
```

## Why you need this lib

> **Q:** I'm a fan of Python and also a fan of maze generation and maze solving algorithms. I have always been jealous of other people's awesome animations of this kind (like [here](https://bl.ocks.org/mbostock/11357811), [here](https://bl.ocks.org/mbostock/c03ee31334ee89abad83) and [here](http://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)), how could I make my own animations with python and share them with other people? (I know `tkinter`, `pyglet` and `pyqt` are nice GUIs but they cannot be published directly to the web ...)

**A:** Now you have this lib `gifmaze` which can help you make even more awesome GIF animations! It has some very nice features:

1. It's written in pure Python, no third-party libs/softwares are required, only built-in modules! (If you want to embed the animation into another image, then `PIL` is required, which is not built-in but comes with all Python distributions, that's all!)

2. It runs very fast and generates optimized GIF files in a few seconds. Usually the output file contains more than one thousand frames but the file size is only around a few hundreds of KBs.

3. You can make GIF animations of all kinds of maze generation and maze solving algorithms on the 2-D grid. 

4. It's fully commented, fully exampled and fully documented!


## A tutorial on this lib


> **Q:** Cool! Is it easy to use?

**A:** Yes! Let me show you with an example:

1. The first thing is to declare a `GIFSurface` object which specifies the size of the image and on which the animation is drawn:
    ```python
    import gifmaze as gm
    
    surface = gm.GIFSurface(600, 400, bg_color=0)
    ```
    Here `bg_color=0` means the 0-th color in the global color table is used as the background color. You may define the global color table at any time except must before you save the image and it must contain at least one (r,g,b) triple. Let's say it's

    ```python
    surface.set_palette([0, 0, 0, 255, 255, 255])
    ```
    So the colors available in the image are black and white. This `surface` is the "bottom layer" object that handles the raw information of the resulting GIF image, i.e. size, palette, loop, and background color.

2. The second task is to declare a `Maze` object which specifies the size and position of the maze and on which the algorithm runs:

    ```python
    maze = gm.Maze(149, 99, mask=None).scale(4).translate((2, 2))
    ```
    Here the size of the maze is 149x99 but is scaled by 4 and translated right and downward by (2, 2), so the top-left pixel of the maze is at (2, 2) and the maze occupies 596x396 pixels. This `maze` is the "top layer" object on which the algorithm runs, it does not know any information about the GIF image.
    
3. The last thing is to define an animation environment to run the algorithm:

    ```python
    from gifmaze.algorithms import random_dfs
    
    anim = gm.Animation(surface)
    anim.pause(100)
    anim.run(random_dfs, maze, speed=15, delay=5, trans_index=None, cmap={0: 0, 1: 1}, mcl=2, start=(0, 0))
    anim.pause(300)
    ```
    So `anim` is the "middle layer" object which calls the renderer to draw the `maze` onto the `surface`. The parameters are:
    + `speed`: controls the speed of the animation.
    + `delay`: controls the delay between successive frames.
    + `trans_index`: the transparent color index.
    + `cmap`: controls how the cells are mapped to colors. Here `cmap={0: 0, 1: 1}` means the cells of state 0 (the walls) are colored with the 0-th color (black), cells of state 1 (the tree) are colored with the 1-th color (white).
    + `mcl`: the minimum code length for initializing the LZW compression.
4. Finally we save the image and finish the animation by

    ```python
    surface.save('random_dfs.gif')
    surface.close()
    ```
The result is shown below (~470 frames, ~65KB):

<p align="center"><img src="https://neozhaoliang.github.io/img/gifmaze/random_dfs.gif"></p>

For more usage please see the `examples/` folder in the github repository. To implement your own maze generation/solving algorithms you may refer to the examples in `algorithms.py`.


## How it works

The most tricky part when implementing this program is that, even for a 2-D grid of a morderate size, there are usually more than one thousand frames in the animation (it's almost always this case when animating Wilson's uniform spanning tree algorithm) and packing such many frames into a GIF image is definitely a formiddable task. So it's quite surprising that our program costs only a few seconds and can produce highly optimized images. The key points are:

1. Find a way to reduce the file size. This is accomplished by maintaining a rectangular region that holds the size and position of current frame and allowing variable mimimum code length for the LZW compression.

2. Make the encoding process as efficient as possible. This is accomplished by using a generator to yield the pixels of the frame instead of repetitively creating/deleting new lists to hold the pixels and send them to the encoder.

3. Write the frames to the file as quickly as possible. This is accomplished by writing them to a in-memory io file first and then flush the data to disk all at once.

Of course you must know how the GIF specifcation works before you could truly understand the code, I will discuss this in the next section.


## References

1. [What's in a gif.](http://www.matthewflickinger.com/lab/whatsinagif/bits_and_bytes.asp) The most helpful and may be the only resource you will need for learning the GIF89a specification.

2. [Maze generation algorithms.](http://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap) A useful webpage for learning various maze generation algorithms. 
