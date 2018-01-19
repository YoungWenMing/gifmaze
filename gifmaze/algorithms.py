# -*- coding: utf-8 -*-

import heapq
import random
from operator import itemgetter
from collections import deque
from .gifmaze import Maze


def prim(maze, renderer, speed=30, start=(0, 0)):
    """Maze by Prim's algorithm."""
    queue = [(0, start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(queue) > 0:
        _, parent, child = heapq.heappop(queue)
        if maze.in_tree(child):
            continue
        maze.mark_cell(child, Maze.TREE)
        maze.mark_space(parent, child, Maze.TREE)
        for v in maze.get_neighbors(child):
            # assign a weight to this edge only when it's needed.
            weight = random.random()
            heapq.heappush(queue, (weight, child, v))

        if maze.num_changes >= speed:
            yield renderer(maze)
   
    if maze.num_changes > 0:
        yield renderer(maze)


def random_dfs(maze, renderer, speed=10, start=(0, 0)):
    """Maze by random depth-first search."""
    stack = [(start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(stack) > 0:
        parent, child = stack.pop()
        if maze.in_tree(child):
            continue
        maze.mark_cell(child, Maze.TREE)
        maze.mark_space(parent, child, Maze.TREE)
        neighbors = maze.get_neighbors(child)
        random.shuffle(neighbors)
        for v in neighbors:
            stack.append((child, v))

        if maze.num_changes >= speed:
            yield renderer(maze)

    if maze.num_changes > 0:
            yield renderer(maze)


def wilson(maze, renderer, speed=50, root=(0, 0)):
    """Maze by Wilson's algorithm."""
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
                    yield renderer(maze)

            # once the walk hits the tree then add its path to the tree.
            maze.mark_path(lerw, Maze.TREE)

    if maze.num_changes > 0:
        yield renderer(maze)


def kruskal(maze, renderer, speed=30):
    """Maze by Kruskal's algorithm."""
    parent = {v: v for v in maze.cells}
    rank = {v: 0 for v in maze.cells}
    edges = [(random.random(), u, v) for u in maze.cells \
             for v in maze.get_neighbors(u) if u < v]

    def find(v):
        """find the root of the subtree that v belongs to."""
        while parent[v] != v:
            v = parent[v]
        return v

    def union(u, v):
        root1 = find(u)
        root2 = find(v)

        if root1 != root2:
            if rank[root1] > rank[root2]:
                parent[root2] = root1

            elif rank[root1] < rank[root2]:
                parent[root1] = root2

            else:
                parent[root1] = root2
                rank[root2] += 1

    for _, u, v in sorted(edges, key=itemgetter(0)):
        if find(u) != find(v):
            union(u, v)
            maze.mark_cell(u, Maze.TREE)
            maze.mark_cell(v, Maze.TREE)
            maze.mark_space(u, v, Maze.TREE)

            if maze.num_changes >= speed:
                yield renderer(maze)
    

    if maze.num_changes > 0:
        yield renderer(maze)


def bfs(maze, renderer, speed=20, start=(0, 0), end=(0, 0)):
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

        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.barrier(child, next_cell)):
                came_from[next_cell] = child
                queue.append((next_cell, dist + 1))
                visited.add(next_cell)

        if maze.num_changes >= speed:
            yield renderer(maze)

    if maze.num_changes > 0:
        yield renderer(maze)

    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)

    maze.mark_path(path, Maze.PATH)
    # show the path
    yield renderer(maze)


def dfs(maze, renderer, speed=20, start=(0, 0), end=(0, 0)):
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
            yield renderer(maze)

    if maze.num_changes > 0:
        yield renderer(maze)

    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)
        
    maze.mark_path(path, Maze.PATH)
    yield renderer(maze)


def astar(maze, renderer, speed=20, start=(0, 0), end=(0, 0)):
    """Solve the maze by A* search."""
    weighted_edges = {(u, v): 1.0 for u in maze.cells for v in maze.get_neighbors(u)}
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
            yield renderer(maze)

    if maze.num_changes > 0:
        yield renderer(maze)

    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)

    maze.mark_path(path, Maze.PATH)
    yield renderer(maze)
