# Dynamic Pathfinding Visualizer

This project is an interactive pathfinding visualizer built using Python and Pygame. It demonstrates how different search strategies behave on a grid, including handling changing environments where obstacles can appear during execution.

## Features

* A* search algorithm
* Greedy Best-First Search
* Manhattan and Euclidean heuristics
* Adjustable heuristic weight
* Random maze generation
* Real-time agent movement
* Dynamic obstacle handling with re-planning
* Displays performance metrics such as nodes visited, path cost, and execution time

## Controls

Mouse:

* Left click to set start node, end node, and walls
* Right click to remove nodes

Buttons:

* Start Search
* Reset Path
* Clear Grid
* Generate Maze
* Toggle Algorithm (A* / Greedy)
* Toggle Heuristic
* Toggle Weight
* Toggle Dynamic Mode

## Tech Stack

* Python 3
* Pygame

## Concepts Used

* Graph search algorithms
* Heuristic-based search
* Priority queues (heap)
* Grid-based pathfinding
* Dynamic replanning

## Notes

Dynamic mode introduces random obstacles while the agent is moving. If the path becomes blocked, the algorithm automatically recalculates a new path from the agent’s current position.
