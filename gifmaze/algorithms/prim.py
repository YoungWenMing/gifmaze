# -*- coding: utf-8 -*-

import heapq
import random
from tqdm import tqdm
from gifmaze.maze import Maze


def prim(maze, render, speed=30, start=(0, 0)):
    """Maze by Prim's algorithm."""
    bar = tqdm(total=len(maze.cells) - 1, desc="Running Prim's algorithm")
    
    queue = [(random.random(), start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(queue) > 0:
        _, parent, child = heapq.heappop(queue)
        if maze.in_tree(child):
            continue

        maze.mark_cell(child, Maze.TREE)
        maze.mark_space(parent, child, Maze.TREE)
        bar.update(1)

        for v in maze.get_neighbors(child):
            # assign a weight to this edge only when it's needed.
            weight = random.random()
            heapq.heappush(queue, (weight, child, v))

        if maze.num_changes >= speed:
            yield render(maze)

    if maze.num_changes > 0:
        yield render(maze)

    bar.close()
