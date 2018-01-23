# -*- coding: utf-8 -*-

import random
from tqdm import tqdm
from gifmaze.maze import Maze


def random_dfs(maze, render, speed=10, start=(0, 0)):
    """Maze by random depth-first search."""
    bar = tqdm(total=len(maze.cells) - 1, desc="Running random depth first search")
    stack = [(start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(stack) > 0:
        parent, child = stack.pop()
        if maze.in_tree(child):
            continue

        maze.mark_cell(child, Maze.TREE)
        maze.mark_space(parent, child, Maze.TREE)
        bar.update(1)

        neighbors = maze.get_neighbors(child)
        random.shuffle(neighbors)
        for v in neighbors:
            stack.append((child, v))

        if maze.num_changes >= speed:
            yield render(maze)

    if maze.num_changes > 0:
        yield render(maze)

    bar.close()
