"""Terminal ASCII visualizer for the maze with real-time user interaction."""

import os
import sys
from typing import List, Set
from mazegen.generator import MazeGenerator
from mazegen.models import Point, Wall


class Visualizer:
    """Renders the maze structure to the terminal and handles user commands."""

    COLOR_RESET = "\033[0m"
    COLOR_WALL = "\033[34m"     # Blue
    COLOR_PATH = "\033[32m"     # Green
    COLOR_ENTRY = "\033[33m"    # Yellow
    COLOR_EXIT = "\033[31m"     # Red
    COLOR_42 = "\033[35m"       # Magenta

    def __init__(self, generator: MazeGenerator) -> None:
        """Initialize visualizer state.

        Args:
            generator: Configured MazeGenerator instance.
        """
        self.generator = generator
        self.show_solution: bool = True

    def run(self) -> None:
        """Start interactive CLI visualization loop."""
        while True:
            self.display()
            print("\n--- Controls ---")
            print("[R] Regenerate | [S] Toggle Solution Path | [Q] Quit")

            try:
                choice = input("Select an option: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting visualizer.")
                break

            if choice == "r":
                self.generator.generate()
            elif choice == "s":
                self.show_solution = not self.show_solution
            elif choice == "q":
                print("Exiting.")
                break

    def display(self) -> None:
        """Render the maze in terminal using ASCII characters."""
        os.system("cls" if os.name == "nt" else "clear")

        solution_cells: Set[Point] = set()
        if self.show_solution:
            solution_cells = self._get_solution_cells()

        grid = self.generator.grid
        width = self.generator.width
        height = self.generator.height

        # Top border
        print(self.COLOR_WALL + "+---" * width + "+" + self.COLOR_RESET)

        for y in range(height):
            # Cell bodies and East/West walls
            row_str = ""
            for x in range(width):
                cell = grid[y][x]
                pt = Point(x, y)

                # West Wall
                if cell.has_wall(Wall.WEST):
                    row_str += f"{self.COLOR_WALL}|{self.COLOR_RESET}"
                else:
                    row_str += " "

                # Cell Interior representation
                if pt == self.generator.entry:
                    row_str += f"{self.COLOR_ENTRY} E {self.COLOR_RESET}"
                elif pt == self.generator.exit:
                    row_str += f"{self.COLOR_EXIT} X {self.COLOR_RESET}"
                elif cell.is_42:
                    row_str += f"{self.COLOR_42} 42{self.COLOR_RESET}"
                elif pt in solution_cells:
                    row_str += f"{self.COLOR_PATH} • {self.COLOR_RESET}"
                else:
                    row_str += "   "

            # Outer East Wall
            row_str += f"{self.COLOR_WALL}|{self.COLOR_RESET}"
            print(row_str)

            # South Walls row
            south_str = ""
            for x in range(width):
                cell = grid[y][x]
                south_str += f"{self.COLOR_WALL}+{self.COLOR_RESET}"
                if cell.has_wall(Wall.SOUTH):
                    south_str += f"{self.COLOR_WALL}---{self.COLOR_RESET}"
                else:
                    south_str += "   "
            south_str += f"{self.COLOR_WALL}+{self.COLOR_RESET}"
            print(south_str)

    def _get_solution_cells(self) -> Set[Point]:
        """Convert solution directions string to a set of solution points."""
        path_str = self.generator.get_shortest_path()
        cells: Set[Point] = {self.generator.entry}

        curr_x, curr_y = self.generator.entry.x, self.generator.entry.y
        for move in path_str:
            if move == "N": curr_y -= 1
            elif move == "E": curr_x += 1
            elif move == "S": curr_y += 1
            elif move == "W": curr_x -= 1
            cells.add(Point(curr_x, curr_y))

        return cells
