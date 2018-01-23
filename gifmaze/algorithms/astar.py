# -*- coding: utf-8 -*-

import heapq
import random
from gifmaze.maze import Maze


def astar(maze, render, speed=20, start=(0, 0), end=(0, 0)):
    """Solve a maze by A* search."""
    weighted_edges = {(u, v): random.random() for u in maze.cells \
                      for v in maze.get_neighbors(u)}
    queue = [(0, start)]
    came_from = {start: start}
    cost_so_far = {start: 0}

    def manhattan(u, v):
        """The heuristic distance between two cells."""
        return abs(u[0] - v[0]) + abs(u[1] - v[1])

    while len(queue) > 0:
        _, child = heapq.heappop(queue)
        parent = came_from[child]
        maze.mark_cell(child, Maze.FILL)
        maze.mark_space(parent, child, Maze.FILL)
        if child == end:
            break

        for next_cell in maze.get_neighbors(child):
            new_cost = cost_so_far[parent] + weighted_edges[(child, next_cell)]
            if (next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]) \
               and (not maze.barrier(next_cell, child)):
                cost_so_far[next_cell] = new_cost
                came_from[next_cell] = child
                priority = new_cost + manhattan(next_cell, end)
                heapq.heappush(queue, (priority, next_cell))

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
    yield render(maze)
