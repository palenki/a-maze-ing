"""Main entry point for the A-Maze-ing maze generator application."""

import sys
from typing import NoReturn

from config_parser import parse_config
from mazegen import MazeGenerator
from visualizer import Visualizer
from writer import write_maze_file

def exit_with_error(massage: str) -> NoReturn:
	"""Print an error message to stderr and exit.
	Args:
		message: Descriptive error message to display.
	"""
	sys.stderr.write("[STDERR] Error: {message}")
	sys.exit(1)


def main() -> None:
	"""Orchestrate the maze generation, file writing, and visualization"""
	if len(sys.argv) != 2:
		exit_with_error("Invalid usage. Syntax: python3 a_maze_ing.py <config.txt>")
	config_filepath: str = sys.argv[1]
	try:
		config = parse_config(config_filepath)
		
		generator = MazeGenerator(
			width=config.width,
			height=config.height,
			entry=(config.entry.x, config.entry.y),
			exit_pt=(config.exit)
		)

		generator.generate()

		write_maze_file(
		filepath=config.output_file,
		grid=generator.grid,
		entry=config.entry,
		exit_pt=config.exit_pt,
		shortest_path=generator.get_shortest_path(),
		)
		
		visualizer = Visualizer(generator=generator)
		visualizer.run()
	
	except FileNotFoundError:
		exit_with_error(f"Configuration file '{config_filepath}' not found.")
	except PermissionError:
		exit_with_error(f"Permission denied reading '{config_filepath}' or writing output.")
	except ValueError as ve:
		exit_with_error(f"Invalid configuration value: {ve}")
	except Exception as exc:
		exit_with_error(f"An unexpected error occurred: {exc}")


if __name__ == "__main__":
	main()
