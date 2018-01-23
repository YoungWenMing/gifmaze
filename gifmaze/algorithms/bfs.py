# -*- coding: utf-8 -*-

from collections import deque
from tqdm import tqdm
from gifmaze.maze import Maze


def bfs(maze, render, speed=20, start=(0, 0), end=(80, 60)):
    """
    Solve a maze by breadth first search.
    The cells are marked by their distance to the starting cell plus three.
    This is because we must distinguish a 'flooded' cell from walls and tree.
    """
    bar = tqdm(total=len(maze.cells) - 1, desc="Solving maze by bfs")
    init_dist = 3
    came_from = {start: start}
    queue = deque([(start, init_dist)])
    maze.mark_cell(start, init_dist)
    visited = set([start])

    while len(queue) > 0:
        child, dist = queue.popleft()
        parent = came_from[child]
        maze.mark_cell(child, dist)
        maze.mark_space(parent, child, dist)
        bar.update(1)

        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.barrier(child, next_cell)):
                came_from[next_cell] = child
                queue.append((next_cell, dist + 1))
                visited.add(next_cell)

        if maze.num_changes >= speed:
            yield render(maze)

    if maze.num_changes > 0:
        yield render(maze)

    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)

    maze.mark_path(path, Maze.PATH)
    # show the path
    yield render(maze)

    bar.close()
