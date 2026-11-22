"""Hexadecimal file exporter for generated mazes."""

from mazegen import MazeGenerator


def write_maze_file(
    filepath: str,
    generator: MazeGenerator
) -> None:
    """Write the maze grid in hexadecimal format and solution metadata."""
    try:
        content: str = generator.to_text()
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as err:
        raise RuntimeError(f"Failed to write output file: {err}") from err
