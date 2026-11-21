"""Package initialization module exposing the core library interface."""

from mazegen.generator import MazeGenerator
from mazegen.models import Cell, Coordinate

__all__ = ["MazeGenerator", "Cell", "Coordinate"]
