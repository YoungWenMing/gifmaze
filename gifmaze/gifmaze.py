# -*- coding: utf-8 -*-
from io import BytesIO
from PIL import Image
from .encoder import Compression, GIFEncoder


class Maze(object):
    """
    This class defines the basic structure of a maze and some operations on it.
    A maze is represented by a grid with `height` rows and `width` columns,
    each cell in the maze has 4 possible states:
    0: it's a wall
    1: it's in the tree
    2: it's in the path
    3: it's filled (this will not be used until the maze-searching animation)
    Initially all cells are walls.
    Adjacent cells in the maze are spaced out by one cell.
    """

    WALL = 0
    TREE = 1
    PATH = 2
    FILL = 3

    def __init__(self, width, height, mask):
        """
        Parameters
        ----------
        width, height: size of the maze, must both be odd integers.

        mask: `None` or an file-like image or an instance of PIL's Image class.
              If not `None` then this mask image must be of binary type:
              the black pixels are considered as `walls` and are overlayed
              on top of the grid graph. Note the walls must preserve the
              connectivity of the grid graph, otherwise the program will
              not terminate.
        """
        if (width * height % 2 == 0):
            raise ValueError('The width and height must both be odd integers.')

        self.width = width
        self.height = height
        self._grid = [[0] * height for _ in range(width)]
        self._num_changes = 0   # a counter holds how many cells are changed.
        self._frame_box = None  # a 4-tuple maintains the region that to be updated.

        if mask is not None:
            if isinstance(mask, Image.Image):
                mask = mask.convert('L').resize((width, height))
            else:
                mask = Image.open(mask).convert('L').resize((width, height))

        def get_mask_pixel(cell):
            return mask is None or mask.getpixel(cell) == 255

        self.cells = []
        for y in range(0, height, 2):
            for x in range(0, width, 2):
                if get_mask_pixel((x, y)):
                    self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 and get_mask_pixel((x - 2, y)):
                neighbors.append((x - 2, y))
            if y >= 2 and get_mask_pixel((x, y - 2)):
                neighbors.append((x, y - 2))
            if x <= width - 3 and get_mask_pixel((x + 2, y)):
                neighbors.append((x + 2, y))
            if y <= height - 3 and get_mask_pixel((x, y + 2)):
                neighbors.append((x, y + 2))
            return neighbors

        self._graph = {v: neighborhood(v) for v in self.cells}
        self.scaling = 1
        self.translation = (0, 0)

    def __str__(self):
        return '{0}({1}x{2})'.format(self.__class__.__name__, self.width, self.height)

    __repr__ = __str__

    def get_neighbors(self, cell):
        return self._graph[cell]

    def mark_cell(self, cell, value):
        """Mark a cell and update `frame_box` and `num_changes`."""
        x, y = cell
        self._grid[x][y] = value
        self._num_changes += 1

        if self._frame_box is not None:
            left, top, right, bottom = self._frame_box
            self._frame_box = (min(x, left),  min(y, top),
                               max(x, right), max(y, bottom))
        else:
            self._frame_box = (x, y, x, y)

    def mark_space(self, c1, c2, value):
        """Mark the space between two adjacent cells."""
        c = ((c1[0] + c2[0]) // 2, (c1[1] + c2[1]) // 2)
        self.mark_cell(c, value)

    def mark_path(self, path, value):
        """Mark the cells in a path and the spaces between them."""
        for cell in path:
            self.mark_cell(cell, value)
        for c1, c2 in zip(path[1:], path[:-1]):
            self.mark_space(c1, c2, value)

    def get_cell(self, cell):
        x, y = cell
        return self._grid[x][y]

    def barrier(self, c1, c2):
        """Check if two adjacent cells are connected."""
        x = (c1[0] + c2[0]) // 2
        y = (c1[1] + c2[1]) // 2
        return self._grid[x][y] == Maze.WALL

    def is_wall(self, cell):
        x, y = cell
        return self._grid[x][y] == Maze.WALL

    def in_tree(self, cell):
        x, y = cell
        return self._grid[x][y] == Maze.TREE

    def in_path(self, cell):
        x, y = cell
        return self._grid[x][y] == Maze.PATH

    def reset(self):
        self._num_changes = 0
        self._frame_box = None

    @property
    def frame_box(self):
        return self._frame_box

    @property
    def num_changes(self):
        return self._num_changes

    def scale(self, c):
        self.scaling = c
        return self
        
    def translate(self, v):
        self.translation = v
        return self



class Renderer(object):
    """
    This class encodes the region specified by the `frame_box` attribute of a maze
    into one frame in the GIF image.
    """
    def __init__(self, cmap, min_code_length):
        """
        cmap: a dict that maps the value of the cells to their color indices.
        
        min_code_length: the minimum code length for the LZW compression.
        """
        self.colormap = {i: i for i in range(1 << min_code_length)}
        self.compress = Compression(min_code_length)
        if cmap:
            self.colormap.update(cmap)

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
        descriptor = GIFEncoder.image_descriptor(maze.scaling * left + maze.translation[0],
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



class GIFSurface(object):
    """
    A GIFSurface is an object on which the animations are drawn,
    and which can be saved as GIF images.
    Each instance opens a BytesIO file in memory onces it's created.
    The frames are temporarily written to this in-memoty file for speed.
    When the animation is finished one should call the `close()` method
    to close the io.
    """
    def __init__(self, width, height, loop=0, bg_color=None):
        """
        ----------
        Parameters
        
        width, height: size of the image in pixels.
        
        loop: number of loops of the image.
        
        bg_color: background color index.
        """
        self.width = width
        self.height = height 
        self.loop = loop
        self._io = BytesIO()
      
        if bg_color is not None:
            self.write(GIFEncoder.rectangle(0, 0, width, height, bg_color))
            
    def write(self, data):
        self._io.write(data)
        
    def set_palette(self, palette):
        """
        Set the global color table of the GIF image.
        """
        palette = bytearray(palette)
        nbits = (len(palette) // 3).bit_length() - 1
        nbits = min(max(nbits, 1), 8)
        valid_len = 3 * (1 << nbits)
        if len(palette) > valid_len:
            palette = palette[:valid_len]
        else:
            palette.extend([0] * (valid_len - len(palette)))

        self.palette = palette
        
    def __str__(self):
        return '{0}({1}x{2}, loop: {3})'.format(self.__class__.__name__,
                                                self.width,
                                                self.height,
                                                self.loop)

    __repr__ = __str__

    @property
    def _gif_header(self):
        """
        Get the `logical screen descriptor`, `global color table`
        and `loop control block`.
        """
        color_depth = (len(self.palette) // 3).bit_length() - 1
        screen = GIFEncoder.screen_descriptor(self.width, self.height, color_depth)
        loop = GIFEncoder.loop_control_block(self.loop)
        return screen + self.palette + loop

    def save(self, filename):
        """
        Save the animation to a .gif file, note the 'wb' mode here!
        """
        with open(filename, 'wb') as f:
            f.write(self._gif_header)
            f.write(self._io.getvalue())
            f.write(bytearray([0x3B]))
            
    def close(self):
        self._io.close()
        
    @classmethod
    def from_image(cls, img_file, loop=0):
        """
        Create a surface from a given image file.
        The size of the returned surface is the same with the image's.
        The image is then painted as the background.
        """
        # the image file usually contains more than 256 colors
        # so we need to convert it to gif format first.
        with BytesIO() as temp_io:
            Image.open(img_file).convert('RGB').save(temp_io, format='gif')
            img = Image.open(temp_io).convert('RGB')
            surface = cls(img.size[0], img.size[1], loop=loop)
            surface.write(GIFEncoder.parse_image(img))           
        return surface



class Animation(object):
    """
    This class is the main entrance for running algorithms.
    """
    
    def __init__(self, surface):
        self._gif_surface = surface
        
    def pause(self, delay, trans_index=0):
        """Pause the animation by padding a 1x1 invisible frame."""
        self._gif_surface.write(GIFEncoder.pause(delay, trans_index))
        
    def paint(self, *args):
        """Paint a rectangular region in the surface."""
        self._gif_surface.write(GIFEncoder.rectangle(*args))
        
    def run(self, algo, maze, delay=5, trans_index=None,
            cmap=None, min_code_length=8, **kwargs):
        """
        The entrance for calling the algorithms.

        --------
        Parameters:


        algo: name of the algorithm.
        
        maze: an instance of the `Maze` class.

        delay: delay time between successive frames.

        trans_index: the transparent channel.
            `None` means there is no transparent color.

        cmap: a dict that maps the values of the cells in a maze
            to their color indices.

        min_code_length: see the doc for the `Compression` class.
        """
        renderer = Renderer(cmap, min_code_length)
        control = GIFEncoder.graphics_control_block(delay, trans_index)
        for frame in algo(maze, renderer, **kwargs):
            self._gif_surface.write(control + frame)
