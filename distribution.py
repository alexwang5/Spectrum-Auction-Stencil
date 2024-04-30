import numpy as np
import itertools
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

def bidder_dfs(num_bidders: int, inter_lists: list, build: list) -> None:
    if (num_bidders == 0):
        # report = frozenset(build)
        # if (report not in seen):
        #     seen.add(report)
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                inter_lists[i, j, int(grid[i, j])] += 1
    else:
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                calc_proximity(center_x=i, center_y=j)
                build.append((i, j))
                bidder_dfs(num_bidders - 1, inter_lists, build)
                build.pop()
                calc_proximity(center_x=i, center_y=j, undo=True)

def average_intersections(inter_lists: list, num_poss: int):
    joint_dist = np.zeros((inter_lists.shape[0], inter_lists.shape[1]))
    for i in range(inter_lists.shape[0]):
        for j in range(inter_lists.shape[1]):
            for k in range(inter_lists.shape[2]):
                joint_dist[i, j] += k * (inter_lists[i, j, k] / num_poss)
    return joint_dist

def calc_distribution(num_bidders: int) -> list:
    inter_lists = np.zeros((3, 6, num_bidders + 1))
    bidder_dfs(num_bidders, inter_lists, list())
    print(18 ** num_bidders)
    joint_dist = average_intersections(inter_lists, 18 ** num_bidders)
    return (inter_lists, joint_dist)

if __name__ == "__main__":
    inter_lists, joint_dist = calc_distribution(5)
    print(inter_lists)
    print("---------")
    print(joint_dist)
    print("---------")

    