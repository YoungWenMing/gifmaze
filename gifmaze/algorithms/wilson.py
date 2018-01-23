# -*- coding: utf-8 -*-

import random
from tqdm import tqdm
from gifmaze.maze import Maze


def wilson(maze, render, speed=50, root=(0, 0)):
    """Maze by Wilson's uniform spanning tree algorithm."""
    bar = tqdm(total=len(maze.cells) - 1, desc="Running Wilson's algorithm")

    def add_to_path(path, cell):
        """
        Add a cell to the path of current random walk.
        Note `path` is modified inside this function.
        """
        maze.mark_cell(cell, Maze.PATH)
        maze.mark_space(path[-1], cell, Maze.PATH)
        path.append(cell)

    def erase_loop(path, cell):
        """
        When a cell is visited twice then a loop is created, erase it.
        Note this function returns a new version of the path.
        """
        index = path.index(cell)
        # erase the loop
        maze.mark_path(path[index:], Maze.WALL)
        maze.mark_cell(path[index], Maze.PATH)
        return path[:index+1]

    # initially the tree contains only the root.
    maze.mark_cell(root, Maze.TREE)

    # for each cell that is not in the tree,
    # start a loop erased random walk from this cell until the walk hits the tree.
    for cell in maze.cells:
        if not maze.in_tree(cell):
            # a list that holds the path of the loop erased random walk.
            lerw = [cell]
            maze.mark_cell(cell, Maze.PATH)
            current_cell = cell

            while not maze.in_tree(current_cell):
                next_cell = random.choice(maze.get_neighbors(current_cell))
                # if it's already in the path then a loop is found.
                if maze.in_path(next_cell):
                    lerw = erase_loop(lerw, next_cell)

                # if the walk hits the tree then finish the walk.
                elif maze.in_tree(next_cell):
                    add_to_path(lerw, next_cell)
                    # `add_to_path` will change the cell to `PATH` so we need to reset it.
                    maze.mark_cell(next_cell, Maze.TREE)

                # continue the walk from this new cell.
                else:
                    add_to_path(lerw, next_cell)

                current_cell = next_cell

                if maze.num_changes >= speed:
                    yield render(maze)

            # once the walk hits the tree then add its path to the tree.
            maze.mark_path(lerw, Maze.TREE)
            bar.update(len(lerw) - 1)

    if maze.num_changes > 0:
        yield render(maze)

    bar.close()
