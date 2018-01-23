# -*- coding: utf-8 -*-

from gifmaze.maze import Maze


def dfs(maze, render, speed=20, start=(0, 0), end=(80, 60)):
    """Solve a maze by dfs."""
    came_from = {start: start}  # a dict to remember each step.
    stack = [start]
    maze.mark_cell(start, Maze.FILL)
    visited = set([start])

    while len(stack) > 0:
        child = stack.pop()
        if child == end:
            break
        parent = came_from[child]
        maze.mark_cell(child, Maze.FILL)
        maze.mark_space(parent, child, Maze.FILL)
        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.barrier(child, next_cell)):
                came_from[next_cell] = child
                stack.append(next_cell)
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
    yield render(maze)
