import numpy as np
from collections import deque

grid = np.zeros((3, 6))
DIRECTIONS = [[1, 0], [-1, 0], [0, 1], [0, -1]]
sz = grid.shape[0] * grid.shape[1]

def check_coord(x: int, y: int) -> bool:
    return (x >= 0 and x < grid.shape[0]) and (y >= 0 and y < grid.shape[1])

def calc_proximity(center_x : int, center_y : int, undo: bool = False) -> None:
    queue = deque()
    seen = set()
    queue.appendleft((center_x, center_y))
    seen.add((center_x, center_y))
    n = 2
    while (n >= 0):
        qLen = len(queue)
        for _ in range(qLen):
            curr = queue.pop()
            if (undo):
                grid[curr[0]][curr[1]] -= 1
            else:
                grid[curr[0]][curr[1]] += 1
            for dir in DIRECTIONS:
                nextX = curr[0] + dir[0]
                nextY = curr[1] + dir[1]
                if (check_coord(nextX, nextY) and not (nextX, nextY) in seen):
                    queue.appendleft((nextX, nextY))
                    seen.add((nextX, nextY))
        n -= 1

def bidder_dfs(num_bidders: int, inter_lists: list, joint_dist: list) -> None:
    if (num_bidders == 0):
        intersects = inter_lists

    else:
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                calc_proximity(center_x=i, center_y=j)
                inter_lists.append(list())
                bidder_dfs(num_bidders - 1, inter_lists, joint_dist)
                inter_lists.pop()
                calc_proximity(center_x=i, center_y=j, undo=True)

def calc_distribution(num_bidders: int) -> list:
    return list()

if __name__ == "__main__":
    calc_distribution(3)