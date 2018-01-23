# -*- coding: utf-8 -*-
"""
`GIFSurface` is the bottom layer object that handles
the information of the output GIF image.
"""
from io import BytesIO
from PIL import Image
from . import encoder


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
        self.palette = None
        self._io = BytesIO()
      
        if bg_color is not None:
            self.write(encoder.rectangle(0, 0, width, height, bg_color))
            
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
            surface.write(encoder.parse_image(img))           
        return surface
            
    def write(self, data):
        self._io.write(data)
        
    def set_palette(self, palette):
        """
        Set the global color table of the GIF image.
        You must specify at least one rgb color in it.
        """
        if isinstance(palette, str):
            palette = self._from_str_colors(palette)
        
        try:
            palette = bytearray(palette)
        except:
            raise ValueError('A 1-d list of integers in range 0-255 is expected.')

        if len(palette) < 3:
            raise ValueError('At least one (r, g, b) triple is required.')

        nbits = (len(palette) // 3).bit_length() - 1
        nbits = min(max(nbits, 1), 8)
        valid_len = 3 * (1 << nbits)
        if len(palette) > valid_len:
            palette = palette[:valid_len]
        else:
            palette.extend([0] * (valid_len - len(palette)))

        self.palette = palette
        
    def _from_str_colors(self, string):
        """Turn a string of colors into a 1-d list."""
        named_colors = {'k': [0, 0, 0],
                        'w': [255, 255, 255],
                        'y': [255, 255, 0],
                        'r': [255, 0, 0],
                        'g': [0, 255 ,0],
                        'b': [0, 0, 255],
                        'c': [0, 255, 255],
                        'm': [255, 0, 255]
                       }
        result = []
        for s in string:
            if s in named_colors:
                result.extend(named_colors[s])
        
        return result

    @property
    def _gif_header(self):
        """
        Get the `logical screen descriptor`, `global color table`
        and `loop control block`.
        """
        if self.palette is None:
            raise ValueError('Missing global color table.')
        
        color_depth = (len(self.palette) // 3).bit_length() - 1
        screen = encoder.screen_descriptor(self.width, self.height, color_depth)
        loop = encoder.loop_control_block(self.loop)
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

    def clear(self, color=None):
        self._io.close()
        self._io = BytesIO()
        if color is not None:
            self._io.write(encoder.rectangle(0, 0, self.width, self.height, color))
