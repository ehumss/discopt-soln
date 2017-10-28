#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import itertools
import time
import numpy as np
import numpy.linalg as LA
from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])


def edge_length(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def cycle_length(cycle, points):
    return sum(edge_length(points[cycle[i - 1]], points[cycle[i]]) for i in range(len(cycle)))


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    point_count = int(lines[0])

    points = []
    for i in range(1, point_count+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # trivial solution
    # visit the points in the order they appear in the file
    # obj, opt, solution = trivial(points)

    # greedy solution (nearest neighbor)
    # starts from 0, add nearest neighbor to the cycle at each step
    # generally acceptable, but can be arbitrarily bad
    # obj, opt, solution = greedy(points)

    # 2-opt solution
    # obj, opt, solution = two_opt(points)

    # k-opt solution
    obj, opt, solution = k_opt(points, 3, time_limit=3600)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def trivial(points):
    cycle = range(len(points))
    return cycle_length(cycle, points), 0, list(cycle)


def greedy(points):
    point_count = len(points)
    coords = np.array([(point.x, point.y) for point in points])
    cycle = [0]
    candidates = set(range(1, point_count))
    while candidates:
        curr_point = cycle[-1]
        nearest_neighbor = None
        nearest_dist = np.inf
        for neighbor in candidates:
            if LA.norm(coords[curr_point] - coords[neighbor]) < nearest_dist:
                nearest_neighbor = neighbor
                nearest_dist = LA.norm(coords[curr_point] - coords[neighbor])
        cycle.append(nearest_neighbor)
        candidates.remove(nearest_neighbor)
    return cycle_length(cycle, points), 0, cycle


def two_swap(cycle, length, start, end, points):
    new_cycle = cycle[:start] + cycle[start:end + 1][::-1] + cycle[end + 1:]
    new_length = length - \
        (edge_length(points[cycle[start - 1]], points[cycle[start]]) +
         edge_length(points[cycle[end]], points[cycle[(end + 1) % len(cycle)]])) + \
        (edge_length(points[new_cycle[start - 1]], points[new_cycle[start]]) +
         edge_length(points[new_cycle[end]], points[new_cycle[(end + 1) % len(cycle)]]))
    return new_cycle, new_length


def two_swap_iteration(cycle, points):
    point_count = len(points)
    length = cycle_length(cycle, points)
    improved = False
    for start, end in itertools.combinations(range(1, point_count), 2):
        new_cycle, new_length = two_swap(cycle, length, start, end, points)
        if new_length < length:
            cycle = new_cycle
            length = new_length
            improved = True
            break
    return cycle, length, improved


def two_opt(points, initial=None, time_limit=None):
    if initial:
        cycle = initial
    else:
        _, _, cycle = greedy(points)
    improved = True
    t = time.clock()
    while improved:
        if time_limit and time.clock() - t >= time_limit:
            break
        cycle, length, improved = two_swap_iteration(cycle, points)
    return cycle_length(cycle, points), 0, cycle


def k_swap(cycle, length, endpoints, points):
    k = len(endpoints) + 1
    segments = [cycle[endpoints[i]:endpoints[i + 1]] for i in range(len(endpoints) - 1)]
    best_cycle = cycle
    best_length = length
    for num_reversed in range(k):
        for reversed_parts in itertools.combinations(range(len(segments)), k):
            new_segments = []
            for i, segment in enumerate(segments):
                if i in reversed_parts:
                    new_segments.append(segment[::-1])
                else:
                    new_segments.append(segment)
            for i, permuted_segments in enumerate(itertools.permutations(new_segments)):
                if num_reversed == 0 and i == 0:
                    continue
                new_cycle = cycle[:endpoints[0]] + \
                    list(itertools.chain.from_iterable(permuted_segments)) + \
                    cycle[endpoints[-1] + 1:]
                new_length = cycle_length(new_cycle, points)
                if new_length < best_length:
                    best_cycle = new_cycle
                    best_length = best_length
    return best_cycle, best_length


def k_swap_iteration(cycle, points, k):
    point_count = len(points)
    length = cycle_length(cycle, points)
    improved = False
    for endpoints in itertools.combinations(range(1, point_count), k):
        new_cycle, new_length = k_swap(cycle, length, endpoints, points)
        # new_cycle, new_length = two_swap(cycle, length, endpoints[0], endpoints[1], points)
        if new_length < length:
            cycle = new_cycle
            length = new_length
            improved = True
            break
    return cycle, length, improved


def k_opt(points, k_max=2, initial=None, time_limit=None):
    if initial:
        cycle = initial
    else:
        _, _, cycle = greedy(points)
    t =  time.clock()
    for k in range(2, k_max + 1):
        improved = True
        while improved:
            if time_limit and time.clock() - t > time_limit:
                break
            cycle, length, improved = k_swap_iteration(cycle, points, k)
    return cycle_length(cycle, points), 0, cycle





if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

