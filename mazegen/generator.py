from collections import deque
from random import Random
from typing import Dict, Iterator, List, Optional, Set, Tuple

Cell = Tuple[int, int]
Step = Tuple[str, int, int, int, int]
DIRECTIONS: Tuple[Step, ...] = (
    ("N", 0, -1, 1, 4),
    ("E", 1, 0, 2, 8),
    ("S", 0, 1, 4, 1),
    ("W", -1, 0, 8, 2),
)
PATTERN = ("#.#.###", "#.#...#", "###.###", "..#.#..", "..#.###")
MAX_CELLS = 100_000


class MazeGenerator:
    """Generate a perfect maze or a braided board with reciprocal wall bits.

    Coordinates use (x, y); grid access is grid[y][x]. Set wall bits mean
    closed: north=1, east=2, south=4, west=8. Fully closed pattern cells
    are excluded from the playable graph. Call generate() before solving.
    """

    def __init__(
        self,
        width: int = 20,
        height: int = 15,
        entry: Cell = (0, 0),
        exit: Optional[Cell] = None,
        perfect: bool = False,
        seed: Optional[int] = None,
        algorithm: str = "dfs",
    ) -> None:
        """Validate parameters and prepare a generator without side effects."""
        if type(width) is not int or type(height) is not int:
            raise ValueError("WIDTH and HEIGHT must be positive integers.")
        if width < 1 or height < 1:
            raise ValueError("WIDTH and HEIGHT must be positive integers.")
        if width * height < 2 or width * height > MAX_CELLS:
            raise ValueError(f"The maze must contain 2 to {MAX_CELLS} cells.")
        if type(perfect) is not bool:
            raise ValueError("PERFECT must be True or False.")
        if seed is not None and type(seed) is not int:
            raise ValueError("SEED must be an integer.")
        if algorithm not in ("dfs", "prim"):
            raise ValueError("ALGORITHM must be dfs or prim.")
        self.width = width
        self.height = height
        self.entry = self._coordinate(entry, "ENTRY")
        default_exit = (width - 1, height - 1)
        self.exit = self._coordinate(default_exit if exit is None else exit,
                                     "EXIT")
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT must be different cells.")
        self.perfect = perfect
        self.seed = seed
        self.algorithm = algorithm
        self.grid: List[List[int]] = []
        self.pattern: Set[Cell] = self._place_pattern()
        self.pattern_omitted = not self.pattern
        self._active: List[Cell] = [
            (x, y) for y in range(height) for x in range(width)
            if (x, y) not in self.pattern
        ]
        potential_edges = sum(
            1 for cell in self._active
            for _, other in self._neighbours(cell)
            if other > cell
        )
        if not perfect and potential_edges - len(self._active) + 1 < 2:
            raise ValueError(
                "PERFECT=False needs space for at least two loops; "
                "use a larger board or PERFECT=True."
            )
        self._rng = Random(seed)

    def _coordinate(self, cell: Cell, name: str) -> Cell:
        """Return a validated coordinate within this maze."""
        valid_tuple = isinstance(cell, tuple) and len(cell) == 2
        if not valid_tuple or any(type(value) is not int for value in cell):
            raise ValueError(f"{name} must be an integer (x, y) tuple.")
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"{name} {cell} is outside the maze.")
        return cell

    def _place_pattern(self) -> Set[Cell]:
        """Place a centred 42 with a corridor margin, avoiding key cells."""
        if self.width < 9 or self.height < 7:
            return set()
        centres = {
            (x, y)
            for x in {(self.width - 1) // 2, self.width // 2}
            for y in {(self.height - 1) // 2, self.height // 2}
        }
        # Try positions closest to the centre first.
        positions = [
            (x, y)
            for y in range(1, self.height - 5)
            for x in range(1, self.width - 7)
        ]
        positions.sort(key=lambda p: (
            abs(2 * p[0] + 7 - self.width)
            + abs(2 * p[1] + 5 - self.height), p[1], p[0]
        ))
        for left, top in positions:
            blocked = {
                (left + x, top + y)
                for y, row in enumerate(PATTERN)
                for x, char in enumerate(row) if char == "#"
            }
            if self.entry in blocked or self.exit in blocked:
                continue
            if not self.perfect and centres <= blocked:
                continue
            if self._connected_without(blocked):
                return blocked
        raise ValueError(
            "The 42 pattern cannot fit with these entry/exit coordinates."
        )

    def _connected_without(self, blocked: Set[Cell]) -> bool:
        """Check that a proposed pattern leaves all corridors connected."""
        reached = {self.entry}
        stack = [self.entry]
        while stack:
            x, y = stack.pop()
            for _, dx, dy, _, _ in DIRECTIONS:
                other = (x + dx, y + dy)
                if (0 <= other[0] < self.width
                        and 0 <= other[1] < self.height
                        and other not in blocked and other not in reached):
                    reached.add(other)
                    stack.append(other)
        return len(reached) == self.width * self.height - len(blocked)

    def _neighbours(self, cell: Cell) -> Iterator[Tuple[Step, Cell]]:
        """Yield in-bounds, non-pattern neighbours in fixed cardinal order."""
        x, y = cell
        for step in DIRECTIONS:
            _, dx, dy, _, _ = step
            nx, ny = x + dx, y + dy
            inside = 0 <= nx < self.width and 0 <= ny < self.height
            if inside and (nx, ny) not in self.pattern:
                yield step, (nx, ny)

    def _open(self, cell: Cell, step: Step, other: Cell) -> None:
        """Open one passage on both sides of a shared wall."""
        self.grid[cell[1]][cell[0]] &= ~step[3]
        self.grid[other[1]][other[0]] &= ~step[4]

    def generate(self, seed: Optional[int] = None) -> List[List[int]]:
        """Generate and return grid[y][x], repeating a configured seed exactly.

        An explicit seed replaces the stored seed. With seed=None stored at
        construction, each call uses fresh system entropy. Mutating the
        returned grid changes this generator's maze.
        """
        if seed is not None:
            if type(seed) is not int:
                raise ValueError("SEED must be an integer.")
            self.seed = seed
        self._rng = Random(self.seed)
        self.grid = [[15] * self.width for _ in range(self.height)]
        if self.algorithm == "dfs":
            self._dfs()
        else:
            self._prim()
        if not self.perfect:
            self._braid()
        return self.grid

    def _dfs(self) -> None:
        """Carve a spanning tree using an iterative random backtracker."""
        visited = {self.entry}
        stack = [self.entry]
        while stack:
            cell = stack[-1]
            choices = [
                (step, other) for step, other in self._neighbours(cell)
                if other not in visited
            ]
            if not choices:
                stack.pop()
                continue
            step, other = self._rng.choice(choices)
            self._open(cell, step, other)
            visited.add(other)
            stack.append(other)

    def _prim(self) -> None:
        """Carve a random spanning tree using an edge frontier."""
        visited = {self.entry}
        frontier = [
            (self.entry, step, other)
            for step, other in self._neighbours(self.entry)
        ]
        while frontier:
            index = self._rng.randrange(len(frontier))
            frontier[index], frontier[-1] = frontier[-1], frontier[index]
            cell, step, other = frontier.pop()
            if other in visited:
                continue
            self._open(cell, step, other)
            visited.add(other)
            frontier.extend(
                (other, direction, neighbour)
                for direction, neighbour in self._neighbours(other)
                if neighbour not in visited
            )

    def passages(self, cell: Cell) -> Iterator[Tuple[str, Cell]]:
        """Yield direction letters and cells reachable through open walls."""
        self._require_generated()
        self._coordinate(cell, "Cell")
        if cell in self.pattern:
            return
        walls = self.grid[cell[1]][cell[0]]
        for step, other in self._neighbours(cell):
            if not walls & step[3]:
                yield step[0], other

    def _degree(self, cell: Cell) -> int:
        """Count open passages incident to a cell."""
        return 4 - self.grid[cell[1]][cell[0]].bit_count()

    def _opens_large_area(self, cell: Cell, step: Step, other: Cell) -> bool:
        """Tentatively open an edge and reject any newly open 3x3 area."""
        self._open(cell, step, other)
        creates_open_area = False
        for top in range(max(0, cell[1] - 2),
                         min(self.height - 3, cell[1]) + 1):
            for left in range(max(0, cell[0] - 2),
                              min(self.width - 3, cell[0]) + 1):
                if self._area_open(left, top):
                    creates_open_area = True
        # Restore the wall after checking the temporary passage.
        self.grid[cell[1]][cell[0]] |= step[3]
        self.grid[other[1]][other[0]] |= step[4]
        return creates_open_area

    def _area_open(self, left: int, top: int) -> bool:
        """Check all twelve interior edges of a 3x3 square."""
        return all(
            not self.grid[y][x] & 2
            for y in range(top, top + 3) for x in range(left, left + 2)
        ) and all(
            not self.grid[y][x] & 4
            for y in range(top, top + 2) for x in range(left, left + 3)
        )

    def _extra_choices(self, cell: Cell) -> List[Tuple[Step, Cell]]:
        """Find closed passages that can safely be opened."""
        return [
            (step, other) for step, other in self._neighbours(cell)
            if self.grid[cell[1]][cell[0]] & step[3]
            and not self._opens_large_area(cell, step, other)
        ]

    def _braid(self) -> None:
        """Remove avoidable dead ends and ensure at least two cycles."""
        cells = list(self._active)
        self._rng.shuffle(cells)
        for cell in cells:
            if self._degree(cell) != 1:
                continue
            choices = self._extra_choices(cell)
            if choices:
                lowest = min(self._degree(other) for _, other in choices)
                step, other = self._rng.choice([
                    choice for choice in choices
                    if self._degree(choice[1]) == lowest
                ])
                self._open(cell, step, other)
        loops = self.loop_count
        if loops >= 2:
            return
        for cell in cells:
            choices = self._extra_choices(cell)
            if choices:
                step, other = self._rng.choice(choices)
                self._open(cell, step, other)
                loops += 1
                if loops >= 2:
                    return
        raise ValueError(
            "Cannot create two loops without an open 3x3 area; "
            "try a larger maze."
        )

    @property
    def loop_count(self) -> int:
        """Return the number of independent cycles in the playable graph."""
        self._require_generated()
        edges = sum(self._degree(cell) for cell in self._active) // 2
        return edges - len(self._active) + 1

    def _require_generated(self) -> None:
        """Reject graph operations before a maze has been generated."""
        if not self.grid:
            raise ValueError("Call generate() before accessing the maze.")

    def solve(self, start: Optional[Cell] = None,
              end: Optional[Cell] = None) -> str:
        """Return a shortest NESW path using breadth-first search."""
        self._require_generated()
        source = self._coordinate(
            self.entry if start is None else start, "Start"
        )
        target = self._coordinate(self.exit if end is None else end, "End")
        if source in self.pattern or target in self.pattern:
            raise ValueError("Path endpoints cannot be inside the 42 pattern.")
        parents: Dict[Cell, Tuple[Cell, str]] = {}
        visited = {source}
        queue = deque([source])
        while queue:
            cell = queue.popleft()
            if cell == target:
                break
            for direction, other in self.passages(cell):
                if other not in visited:
                    visited.add(other)
                    parents[other] = (cell, direction)
                    queue.append(other)
        if target not in visited:
            raise ValueError("No path exists between the requested endpoints.")
        # Rebuild the path by following parents from the target to the start.
        letters: List[str] = []
        while target != source:
            target, direction = parents[target]
            letters.append(direction)
        return "".join(reversed(letters))

    def solution_cells(self) -> List[Cell]:
        """Return shortest-route coordinates, including both endpoints."""
        cell = self.entry
        cells = [cell]
        offsets = {letter: (dx, dy) for letter, dx, dy, _, _ in DIRECTIONS}
        for letter in self.solve():
            dx, dy = offsets[letter]
            cell = (cell[0] + dx, cell[1] + dy)
            cells.append(cell)
        return cells

    def to_text(self) -> str:
        """Serialize the exact subject format, with LF-terminated lines."""
        self._require_generated()
        rows = ["".join(f"{walls:X}" for walls in row) for row in self.grid]
        rows.extend([
            "", f"{self.entry[0]},{self.entry[1]}",
            f"{self.exit[0]},{self.exit[1]}", self.solve(),
        ])
        return "\n".join(rows) + "\n"
