"""Maze generation and pathfinding module."""

from collections import deque
import random
from typing import Dict, List, Optional, Set, Tuple

from mazegen.models import Cell, Coordinate


# 5 rows x 7 columns bitmap representing "42"
PATTERN_42: List[List[int]] = [
    [1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],
]


class MazeGenerator:
    """Generates perfect or Pac-Man style mazes with a '42' pattern."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pt: Tuple[int, int],
        perfect: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize the maze generator and validate basic parameters."""
        if width < 3 or height < 3:
            raise ValueError("Maze dimensions must be at least 3x3.")
        if entry == exit_pt:
            raise ValueError("Entry and exit coordinates must be different.")

        self.width: int = width
        self.height: int = height
        self.entry: Coordinate = Coordinate(entry[0], entry[1])
        self.exit: Coordinate = Coordinate(exit_pt[0], exit_pt[1])
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self._rng: random.Random = random.Random(seed)

        if not self._in_bounds(self.entry.x, self.entry.y):
            raise ValueError("Entry coordinates are out of bounds.")
        if not self._in_bounds(self.exit.x, self.exit.y):
            raise ValueError("Exit coordinates are out of bounds.")

        self.grid: List[List[Cell]] = []
        self.pattern_42_placed: bool = False
        self.solution: str = ""

    def generate(self) -> List[List[Cell]]:
        """Generate the maze grid and compute the shortest path."""
        self.grid = [
            [Cell() for _ in range(self.width)] for _ in range(self.height)
        ]
        visited: Set[Coordinate] = set()

        # 1. Place the "42" closed cells in the center if it fits
        self._apply_42_pattern(visited)

        # Ensure entry and exit were not blocked by the "42" pattern
        if self.entry in visited or self.exit in visited:
            raise ValueError(
                "Entry or exit overlaps with the central '42' pattern."
            )

        # 2. Carve a spanning tree (perfect maze) using iterative backtracker
        self._carve_perfect_maze(visited)

        # 3. If not perfect, convert into a playable Pac-Man style board
        if not self.perfect:
            self._make_playable_board()

        # 4. Find the shortest path from entry to exit
        self.solution = self._find_shortest_path()
        if not self.solution and self.entry != self.exit:
            raise RuntimeError("Failed to find a valid path to the exit.")

        return self.grid

    def _in_bounds(self, x: int, y: int) -> bool:
        """Check whether (x, y) is inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _apply_42_pattern(self, visited: Set[Coordinate]) -> None:
        """Mark the '42' pattern cells as closed and visited if possible."""
        pat_h = len(PATTERN_42)
        pat_w = len(PATTERN_42[0])

        # Need at least 2 cells of margin around the pattern
        if self.width < pat_w + 4 or self.height < pat_h + 4:
            self.pattern_42_placed = False
            return

        start_x = (self.width - pat_w) // 2
        start_y = (self.height - pat_h) // 2

        for r in range(pat_h):
            for c in range(pat_w):
                if PATTERN_42[r][c] == 1:
                    cx, cy = start_x + c, start_y + r
                    self.grid[cy][cx].is_42 = True
                    visited.add(Coordinate(cx, cy))

        self.pattern_42_placed = True

    def _remove_wall(self, c1: Coordinate, c2: Coordinate) -> None:
        """Remove the shared wall between two adjacent cells."""
        dx = c2.x - c1.x
        dy = c2.y - c1.y

        if dx == 1:
            self.grid[c1.y][c1.x].east = False
            self.grid[c2.y][c2.x].west = False
        elif dx == -1:
            self.grid[c1.y][c1.x].west = False
            self.grid[c2.y][c2.x].east = False
        elif dy == 1:
            self.grid[c1.y][c1.x].south = False
            self.grid[c2.y][c2.x].north = False
        elif dy == -1:
            self.grid[c1.y][c1.x].north = False
            self.grid[c2.y][c2.x].south = False

    def _carve_perfect_maze(self, visited: Set[Coordinate]) -> None:
        """Generate a perfect maze using iterative depth-first search."""
        stack: List[Coordinate] = [self.entry]
        visited.add(self.entry)

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        while stack:
            current = stack[-1]
            neighbors: List[Coordinate] = []

            for dx, dy in directions:
                nx, ny = current.x + dx, current.y + dy
                neighbor = Coordinate(nx, ny)
                if self._in_bounds(nx, ny) and neighbor not in visited:
                    neighbors.append(neighbor)

            if neighbors:
                chosen = self._rng.choice(neighbors)
                self._remove_wall(current, chosen)
                visited.add(chosen)
                stack.append(chosen)
            else:
                stack.pop()

    def _creates_3x3_open_area(self, x: int, y: int) -> bool:
        """Check if opening walls around (x, y) creates a 3x3 open block."""
        for top_y in range(max(0, y - 2), min(self.height - 2, y + 1)):
            for left_x in range(max(0, x - 2), min(self.width - 2, x + 1)):
                if self._is_3x3_completely_open(left_x, top_y):
                    return True
        return False

    def _is_3x3_completely_open(self, left_x: int, top_y: int) -> bool:
        """Return True if all internal walls inside a 3x3 area are open."""
        for r in range(top_y, top_y + 3):
            for c in range(left_x, left_x + 3):
                cell = self.grid[r][c]
                if cell.is_42:
                    return False
                if c < left_x + 2 and cell.east:
                    return False
                if r < top_y + 2 and cell.south:
                    return False
        return True

    def _try_open_wall(self, c1: Coordinate, c2: Coordinate) -> bool:
        """Safely open a wall if neither cell is '42' and no 3x3 is formed."""
        if not self._in_bounds(c2.x, c2.y):
            return False
        cell1 = self.grid[c1.y][c1.x]
        cell2 = self.grid[c2.y][c2.x]
        if cell1.is_42 or cell2.is_42:
            return False

        # Save previous state to rollback if 3x3 rule is violated
        old1 = (cell1.north, cell1.east, cell1.south, cell1.west)
        old2 = (cell2.north, cell2.east, cell2.south, cell2.west)

        self._remove_wall(c1, c2)
        if self._creates_3x3_open_area(c1.x, c1.y) or (
            self._creates_3x3_open_area(c2.x, c2.y)
        ):
            cell1.north, cell1.east, cell1.south, cell1.west = old1
            cell2.north, cell2.east, cell2.south, cell2.west = old2
            return False
        return True

    def _make_playable_board(self) -> None:
        """Open dead-ends, corners, and center to create loops (Pac-Man mode)."""
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # 1. Open dead-ends (cells with 3 closed walls)
        coords = [
            Coordinate(x, y)
            for y in range(self.height)
            for x in range(self.width)
        ]
        self._rng.shuffle(coords)

        for coord in coords:
            cell = self.grid[coord.y][coord.x]
            if cell.is_42:
                continue
            walls = sum([cell.north, cell.east, cell.south, cell.west])
            if walls >= 3:
                shuffled_dirs = list(directions)
                self._rng.shuffle(shuffled_dirs)
                for dx, dy in shuffled_dirs:
                    neighbor = Coordinate(coord.x + dx, coord.y + dy)
                    if self._try_open_wall(coord, neighbor):
                        break

        # 2. Ensure four corners and center have open corridors (at least 2 exits)
        key_points = [
            Coordinate(0, 0),
            Coordinate(self.width - 1, 0),
            Coordinate(0, self.height - 1),
            Coordinate(self.width - 1, self.height - 1),
            Coordinate(self.width // 2, self.height // 2),
        ]
        for pt in key_points:
            cell = self.grid[pt.y][pt.x]
            if cell.is_42:
                continue
            open_sides = 4 - sum([cell.north, cell.east, cell.south, cell.west])
            if open_sides < 2:
                for dx, dy in directions:
                    if self._try_open_wall(pt, Coordinate(pt.x + dx, pt.y + dy)):
                        open_sides += 1
                        if open_sides >= 2:
                            break

    def _find_shortest_path(self) -> str:
        """Find the shortest path from entry to exit using BFS."""
        queue: deque[Coordinate] = deque([self.entry])
        came_from: Dict[Coordinate, Optional[Tuple[Coordinate, str]]] = {
            self.entry: None
        }

        moves = [
            ("N", 0, -1, "north"),
            ("E", 1, 0, "east"),
            ("S", 0, 1, "south"),
            ("W", -1, 0, "west"),
        ]

        while queue:
            current = queue.popleft()
            if current == self.exit:
                break

            cell = self.grid[current.y][current.x]
            for letter, dx, dy, wall_attr in moves:
                if not getattr(cell, wall_attr):
                    nxt = Coordinate(current.x + dx, current.y + dy)
                    if self._in_bounds(nxt.x, nxt.y) and nxt not in came_from:
                        came_from[nxt] = (current, letter)
                        queue.append(nxt)

        if self.exit not in came_from:
            return ""

        path_letters: List[str] = []
        curr: Optional[Coordinate] = self.exit
        while curr is not None and came_from[curr] is not None:
            prev_info = came_from[curr]
            if prev_info is not None:
                prev_coord, letter = prev_info
                path_letters.append(letter)
                curr = prev_coord

        path_letters.reverse()
        return "".join(path_letters)
