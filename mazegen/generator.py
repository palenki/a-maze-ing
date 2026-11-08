"""Maze generation algorithms and shortest-path calculation module."""

from collections import deque
import random
from typing import Dict, List, Optional, Set, Tuple

from mazegen.models import Cell, Point, Wall


class MazeGenerator:
    """Core maze generator implementing perfect and Pac-Man generation algorithms."""

    # 5x7 matrix definition for '4' and '2' block patterns
    PATTERN_42: List[List[int]] = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pt: Tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize the maze generator configuration.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: Entry point (x, y).
            exit_pt: Exit point (x, y).
            perfect: If True, creates a single-path maze. If False, creates a Pac-Man board.
            seed: Optional random seed for reproducible generation.
        """
        self.width: int = width
        self.height: int = height
        self.entry: Point = Point(*entry)
        self.exit: Point = Point(*exit_pt)
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed

        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

        if seed is not None:
            random.seed(seed)

    def generate(self) -> None:
        """Generate the complete maze structure according to requirements."""
        self._carve_pattern_42()
        self._generate_base_tree()

        if not self.perfect:
            self._apply_pacman_rules()

    def _carve_pattern_42(self) -> None:
        """Attempt to engrave fully closed '42' cells into the center of the grid."""
        pat_h = len(self.PATTERN_42)
        pat_w = len(self.PATTERN_42[0])

        if self.width < pat_w + 2 or self.height < pat_h + 2:
            print("Warning: Grid size too small for '42' pattern.", flush=True)
            return

        start_x = (self.width - pat_w) // 2
        start_y = (self.height - pat_h) // 2

        for r in range(pat_h):
            for c in range(pat_w):
                if self.PATTERN_42[r][c] == 1:
                    cell = self.grid[start_y + r][start_x + c]
                    cell.is_42 = True
                    cell.visited = True
                    cell.walls = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST

    def _generate_base_tree(self) -> None:
        """Generate base maze structure using Randomized Depth-First Search."""
        stack: List[Cell] = []
        start_cell = self._get_unvisited_start()
        if not start_cell:
            return

        start_cell.visited = True
        stack.append(start_cell)

        while stack:
            current = stack[-1]
            neighbors = self._get_unvisited_neighbors(current)

            if neighbors:
                neighbor, wall_curr, wall_neigh = random.choice(neighbors)
                current.remove_wall(wall_curr)
                neighbor.remove_wall(wall_neigh)
                neighbor.visited = True
                stack.append(neighbor)
            else:
                stack.pop()

    def _get_unvisited_start(self) -> Optional[Cell]:
        """Find the first non-'42' cell to start generation."""
        for r in range(self.height):
            for c in range(self.width):
                if not self.grid[r][c].visited:
                    return self.grid[r][c]
        return None

    def _get_unvisited_neighbors(self, cell: Cell) -> List[Tuple[Cell, Wall, Wall]]:
        """Get accessible unvisited adjacent cells with corresponding walls."""
        neighbors: List[Tuple[Cell, Wall, Wall]] = []
        directions = [
            (0, -1, Wall.NORTH, Wall.SOUTH),
            (1, 0, Wall.EAST, Wall.WEST),
            (0, 1, Wall.SOUTH, Wall.NORTH),
            (-1, 0, Wall.WEST, Wall.EAST),
        ]

        for dx, dy, w_curr, w_neigh in directions:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                target = self.grid[ny][nx]
                if not target.visited and not target.is_42:
                    neighbors.append((target, w_curr, w_neigh))

        return neighbors

    def _apply_pacman_rules(self) -> None:
        """Adjust maze layout to conform to Pac-Man board requirements."""
        # 1. Clear corners and center
        corners = [
            (0, 0), (self.width - 1, 0),
            (0, self.height - 1), (self.width - 1, self.height - 1)
        ]
        center = (self.width // 2, self.height // 2)

        for cx, cy in corners + [center]:
            self._open_surrounding_walls(cx, cy)

        # 2. Break additional walls to create loops and remove dead-ends
        self._remove_dead_ends()

    def _open_surrounding_walls(self, x: int, y: int) -> None:
        """Remove external walls around specific key zones if possible."""
        cell = self.grid[y][x]
        directions = [
            (0, -1, Wall.NORTH, Wall.SOUTH),
            (1, 0, Wall.EAST, Wall.WEST),
            (0, 1, Wall.SOUTH, Wall.NORTH),
            (-1, 0, Wall.WEST, Wall.EAST),
        ]
        for dx, dy, w_curr, w_neigh in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbor = self.grid[ny][nx]
                if not neighbor.is_42 and not cell.is_42:
                    cell.remove_wall(w_curr)
                    neighbor.remove_wall(w_neigh)
                    break

    def _remove_dead_ends(self) -> None:
        """Open dead-end corridors to guarantee multiple independent paths."""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.is_42:
                    continue

                # Count closed walls
                closed = [w for w in Wall if cell.has_wall(w)]
                if len(closed) == 3:  # Dead-end cell
                    for w in closed:
                        dx, dy = 0, 0
                        if w == Wall.NORTH: dy = -1
                        elif w == Wall.EAST: dx = 1
                        elif w == Wall.SOUTH: dy = 1
                        elif w == Wall.WEST: dx = -1

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            neighbor = self.grid[ny][nx]
                            if not neighbor.is_42:
                                opposite = self._opposite_wall(w)
                                cell.remove_wall(w)
                                neighbor.remove_wall(opposite)
                                break

    @staticmethod
    def _opposite_wall(wall: Wall) -> Wall:
        """Return opposite cardinal direction wall."""
        mapping = {
            Wall.NORTH: Wall.SOUTH,
            Wall.EAST: Wall.WEST,
            Wall.SOUTH: Wall.NORTH,
            Wall.WEST: Wall.EAST,
        }
        return mapping[wall]

    def get_shortest_path(self) -> str:
        """Find the shortest valid solution path from entry to exit using BFS.

        Returns:
            String of cardinal directions (e.g., 'NNERRSSW').
        """
        queue: deque[Point] = deque([self.entry])
        came_from: Dict[Point, Tuple[Point, str]] = {}
        visited: Set[Point] = {self.entry}

        directions = [
            (0, -1, Wall.NORTH, "N"),
            (1, 0, Wall.EAST, "E"),
            (0, 1, Wall.SOUTH, "S"),
            (-1, 0, Wall.WEST, "W"),
        ]

        while queue:
            curr = queue.popleft()
            if curr == self.exit:
                break

            cell = self.grid[curr.y][curr.x]

            for dx, dy, wall, char in directions:
                if not cell.has_wall(wall):
                    nx, ny = curr.x + dx, curr.y + dy
                    nxt = Point(nx, ny)
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if nxt not in visited and not self.grid[ny][nx].is_42:
                            visited.add(nxt)
                            came_from[nxt] = (curr, char)
                            queue.append(nxt)

        # Reconstruct path
        path: List[str] = []
        curr_pt = self.exit
        while curr_pt != self.entry:
            if curr_pt not in came_from:
                return ""  # Path not found
            parent, char = came_from[curr_pt]
            path.append(char)
            curr_pt = parent

        return "".join(reversed(path))
