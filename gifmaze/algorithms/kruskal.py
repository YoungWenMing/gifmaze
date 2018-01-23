# -*- coding: utf-8 -*-

import random
from operator import itemgetter
from tqdm import tqdm
from gifmaze.maze import Maze


def kruskal(maze, render, speed=30):
    """Maze by Kruskal's algorithm."""
    bar = tqdm(total=len(maze.cells) - 1, desc="Running Kruskal's algorithm")
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
            bar.update(1)
            if maze.num_changes >= speed:
                yield render(maze)

    if maze.num_changes > 0:
        yield render(maze)

    bar.close()
