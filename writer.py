"""Module responsible for writing maze output to file in hexadecimal format."""

from typing import List
from mazegen.models import Cell, Point


def write_maze_file(
    filepath: str,
    grid: List[List[Cell]],
    entry: Point,
    exit_pt: Point,
    shortest_path: str,
) -> None:
    """Export maze wall grid and metadata to output file using context manager.

    Args:
        filepath: Destination file path.
        grid: 2D matrix of Cell objects.
        entry: Entry point coordinates.
        exit_pt: Exit point coordinates.
        shortest_path: Solution directions string.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        # 1. Write hexadecimal wall representation row by row
        for row in grid:
            hex_row = "".join(cell.to_hex() for cell in row)
            file.write(f"{hex_row}\n")

        # 2. Empty line separator
        file.write("\n")

        # 3. Entry, Exit, and Shortest path metadata
        file.write(f"{entry.x},{entry.y}\n")
        file.write(f"{exit_pt.x},{exit_pt.y}\n")
        file.write(f"{shortest_path}\n")
