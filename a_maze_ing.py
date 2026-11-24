"""Main CLI entry point for A-Maze-ing."""

import sys
from typing import Optional

from config_parser import MazeConfig, parse_config
from mazegen import MazeGenerator
from visualizer import render_maze, clear_screen
from writer import write_maze_file


def build_and_save(
    config: MazeConfig, seed_override: Optional[int] = None
) -> MazeGenerator:
    """Instantiate generator, create maze, and write output file."""
    active_seed: int | None = (
        seed_override if seed_override is not None else config.seed
    )

    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_pt=config.exit_pt,
        perfect=config.perfect,
        seed=active_seed,
        algorithm=config.algorithm,
    )
    generator.generate()
    write_maze_file(filepath=config.output_file, generator=generator)
    return generator


def interactive_loop(config: MazeConfig, generator: MazeGenerator) -> None:
    """Run the interactive terminal menu."""
    show_path: bool = True
    color_index: int = 0
    regen_count: int = 0

    while True:
        path_cells: set[tuple[int, int]] = set(generator.solution_cells())
        render_maze(
            grid=generator.grid,
            entry=config.entry,
            exit_pt=config.exit_pt,
            pattern_cells=generator.pattern,
            path_cells=path_cells,
            show_path=show_path,
            color_index=color_index,
        )
        if generator.pattern_omitted:
            print("Warning: Maze is too small to display the 42 pattern.")
        print("\n1. Re-generate a new maze")
        print("2. Show/Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")

        try:
            choice: str = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            clear_screen()
            break

        if choice == "1":
            regen_count += 1
            new_seed = (
                config.seed + regen_count if config.seed is not None else None
            )
            generator = build_and_save(config, seed_override=new_seed)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index += 1
        elif choice == "4":
            print("Goodbye!")
            clear_screen()
            break
        else:
            print("Invalid option. Please enter a number between 1 and 4.")


def main() -> None:
    """Parse arguments, run maze generation, and launch UI."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    try:
        config: MazeConfig = parse_config(sys.argv[1])
        generator: MazeGenerator = build_and_save(config)
        interactive_loop(config, generator)
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
