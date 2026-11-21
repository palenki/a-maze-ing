"""Data structures for the maze representation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    """Represents an (x, y) coordinate in the maze grid."""

    x: int
    y: int


@dataclass
class Cell:
    """Represents a single cell with four cardinal walls.

    True means the wall is closed; False means it is open.
    """

    north: bool = True
    east: bool = True
    south: bool = True
    west: bool = True
    is_42: bool = False

    def is_fully_closed(self) -> bool:
        """Return True if all four walls are closed."""
        return self.north and self.east and self.south and self.west

    def to_hex(self) -> str:
        """Convert wall states into a single hexadecimal character.

        Bit 0 (1): North
        Bit 1 (2): East
        Bit 2 (4): South
        Bit 3 (8): West
        """
        value = 0
        if self.north:
            value += 1
        if self.east:
            value += 2
        if self.south:
            value += 4
        if self.west:
            value += 8
        return format(value, "x")
