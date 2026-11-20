"""Terminal visualizer with fixed distinct high-contrast colors for entry, exit, and pattern 42."""

import os
from typing import Dict, List, Set
from mazegen.generator import MazeGenerator
from mazegen.models import Point, Wall


class Visualizer:
    """Renders a compact maze with distinct color themes for walls and path components."""

    # Color themes for Walls and Solution Path
    COLOR_PALETTES: List[Dict[str, str]] = [
        {"wall": "\033[34m", "path": "\033[92\033[1m"},  # Blue Wall / Green Path
        {"wall": "\033[36m", "path": "\033[93\033[1m"},  # Cyan Wall / Yellow Path
        {"wall": "\033[32m", "path": "\033[95\033[1m"},  # Green Wall / Magenta Path
        {"wall": "\033[35m", "path": "\033[96\033[1m"},  # Magenta Wall / Cyan Path
        {"wall": "\033[37m", "path": "\033[91\033[1m"},  # White Wall / Red Path
    ]

    COLOR_RESET: str = "\033[0m"
    COLOR_ENTRY: str = "\033[93\033[1m"  # Bright Yellow Bold (Entry)
    COLOR_EXIT: str = "\033[91\033[1m"   # Bright Red Bold (Exit)
    COLOR_42: str = "\033[95\033[1m"     # Bright Magenta Bold (Fixed 42 Pattern)

    def __init__(self, generator: MazeGenerator) -> None:
        """Initialize visualizer state and color controls.

        Args:
            generator: Instance of configured MazeGenerator.
        """
        self.generator = generator
        self.show_solution: bool = True
        self.palette_index: int = 0

    @property
    def current_palette(self) -> Dict[str, str]:
        """Get currently active color palette."""
        return self.COLOR_PALETTES[self.palette_index]

    def run(self) -> None:
        """Start CLI interactive visualization loop."""
        while True:
            self.display()
            print("\n--- Controls ---")
            print("[R] Regenerate | [S] Toggle Solution Path | [C] Change Theme Colors | [Q] Quit")

            try:
                choice = input("Option: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting visualizer.")
                break

            if choice == "r":
                if self.generator.seed is not None:
                    self.generator.seed += 1
                self.generator.generate()
            elif choice == "s":
                self.show_solution = not self.show_solution
            elif choice == "c":
                self.palette_index = (self.palette_index + 1) % len(self.COLOR_PALETTES)
            elif choice == "q":
                print("Exiting.")
                break

    def display(self) -> None:
        """Render compact maze using distinct colors for walls, 42 pattern, entry, and path."""
        os.system("cls" if os.name == "nt" else "clear")

        solution_cells: Set[Point] = set()
        if self.show_solution:
            solution_cells = self._get_solution_cells()

        grid = self.generator.grid
        width = self.generator.width
        height = self.generator.height

        palette = self.current_palette
        wc = palette["wall"]
        path_color = palette["path"]

        # Top border using +--
        print(wc + "+--" * width + "+" + self.COLOR_RESET)

        for y in range(height):
            # 1. Cell content and West vertical walls
            row_str = ""
            for x in range(width):
                cell = grid[y][x]
                pt = Point(x, y)

                # West Wall
                if cell.has_wall(Wall.WEST):
                    row_str += f"{wc}|{self.COLOR_RESET}"
                else:
                    row_str += " "

                # Priority formatting: Entry/Exit > 42 Pattern > Solution Path > Empty
                if pt == self.generator.entry:
                    row_str += f"{self.COLOR_ENTRY}E {self.COLOR_RESET}"
                elif pt == self.generator.exit:
                    row_str += f"{self.COLOR_EXIT}X {self.COLOR_RESET}"
                elif cell.is_42:
                    row_str += f"{self.COLOR_42}42{self.COLOR_RESET}"  # Distinct Magenta
                elif pt in solution_cells:
                    row_str += f"{path_color}••{self.COLOR_RESET}"
                else:
                    row_str += "  "

            # Outer East Wall
            row_str += f"{wc}|{self.COLOR_RESET}"
            print(row_str)

            # 2. Intersections and South horizontal walls (+--)
            south_str = ""
            for x in range(width):
                cell = grid[y][x]
                south_str += f"{wc}+{self.COLOR_RESET}"
                if cell.has_wall(Wall.SOUTH):
                    south_str += f"{wc}--{self.COLOR_RESET}"
                else:
                    south_str += "  "
            south_str += f"{wc}+{self.COLOR_RESET}"
            print(south_str)

    def _get_solution_cells(self) -> Set[Point]:
        """Convert shortest path direction sequence to a set of coordinate Points."""
        path_str = self.generator.get_shortest_path()
        cells: Set[Point] = {self.generator.entry}

        curr_x, curr_y = self.generator.entry.x, self.generator.entry.y
        for move in path_str:
            if move == "N":
                curr_y -= 1
            elif move == "E":
                curr_x += 1
            elif move == "S":
                curr_y += 1
            elif move == "W":
                curr_x -= 1
            cells.add(Point(curr_x, curr_y))

        return cells
