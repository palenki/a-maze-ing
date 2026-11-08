"""Package initialization module exposing the core library interface."""

from mazegen.generator import MazeGenerator
from mazegen.models import Cell, Point, Wall

__all__ = ["MazeGenerator", "Cell", "Point", "Wall"]
