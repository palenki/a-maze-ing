"""Data models and enumerations for the maze generator library."""

from dataclasses import dataclass
from enum import IntFlag


class Wall(IntFlag):
    """Bitmask representing walls in cardinal directions."""

    NORTH = 1  # Bit 0 (LSB)
    EAST = 2   # Bit 1
    SOUTH = 4  # Bit 2
    WEST = 8   # Bit 3


@dataclass(frozen=True)
class Point:
    """Immutable 2D coordinate representation."""

    x: int
    y: int


class Cell:
    """Represents an individual cell within the maze grid.

    Attributes:
        x: X-coordinate of the cell.
        y: Y-coordinate of the cell.
        walls: Bitmask representing active closed walls.
        visited: Flag for maze generation algorithms.
        is_42: Flag indicating if this cell is part of the '42' pattern.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialize a Cell at specified coordinates with all walls closed.

        Args:
            x: X-coordinate.
            y: Y-coordinate.
        """
        self.x: int = x
        self.y: int = y
        self.walls: int = Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST
        self.visited: bool = False
        self.is_42: bool = False

    def remove_wall(self, wall: Wall) -> None:
        """Open a wall on the specified cardinal direction.

        Args:
            wall: Cardinal direction wall to open.
        """
        self.walls &= ~wall.value

    def has_wall(self, wall: Wall) -> bool:
        """Check if a wall is closed in the specified direction.

        Args:
            wall: Cardinal direction wall to check.

        Returns:
            True if the wall is closed, False otherwise.
        """
        return bool(self.walls & wall.value)

    def to_hex(self) -> str:
        """Convert closed walls bitmask to a uppercase hexadecimal character.

        Returns:
            Single hexadecimal string character (0-F).
        """
        return f"{self.walls:X}"
