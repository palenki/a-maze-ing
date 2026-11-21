"""Hexadecimal file exporter for generated mazes."""

from mazegen.models import Cell


def write_maze_file(
    filepath: str,
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit_pt: tuple[int, int],
    solution: str,
) -> None:
    """Write the maze grid in hexadecimal format and solution metadata."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            for row in grid:
                hex_line = "".join(cell.to_hex() for cell in row)
                file.write(f"{hex_line}\n")

            file.write("\n")
            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit_pt[0]},{exit_pt[1]}\n")
            file.write(f"{solution}\n")
    except OSError as exc:
        raise RuntimeError(f"Failed to write output file: {exc}") from exc
