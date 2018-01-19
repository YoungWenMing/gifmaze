"""

 ██████╗ ██╗███████╗███╗   ███╗ █████╗ ███████╗███████╗
██╔════╝ ██║██╔════╝████╗ ████║██╔══██╗╚══███╔╝██╔════╝
██║  ███╗██║█████╗  ██╔████╔██║███████║  ███╔╝ █████╗  
██║   ██║██║██╔══╝  ██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  
╚██████╔╝██║██║     ██║ ╚═╝ ██║██║  ██║███████╗███████╗
 ╚═════╝ ╚═╝╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
                                                       
"""
from .encoder import Compression, GIFEncoder
from .gifmaze import Maze, Renderer, GIFSurface, Animation
from . import algorithms
from .gentext import generate_text_mask
