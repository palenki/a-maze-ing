"""Main CLI entry point for A-Maze-ing."""

import sys
from typing import Optional

from config_parser import MazeConfig, parse_config
from mazegen import MazeGenerator
from visualizer import render_maze
from writer import write_maze_file


def build_and_save(
    config: MazeConfig, seed_override: Optional[int] = None
) -> MazeGenerator:
    """Instantiate generator, create maze, and write output file."""
    active_seed: int | None = seed_override if seed_override is not None else config.seed

    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_pt=config.exit_pt,
        perfect=config.perfect,
        seed=active_seed,
    )
    grid: list[list[Cell]] = generator.generate()

    if not generator.pattern_42_placed:
        print(
            "Warning: Maze is too small to display the '42' pattern.",
            file=sys.stderr,
        )

    write_maze_file(
        filepath=config.output_file,
        grid=grid,
        entry=config.entry,
        exit_pt=config.exit_pt,
        solution=generator.solution,
    )
    return generator


def clear_screen() -> None:
    """Clear the terminal screen, scrollback buffer, and move cursor to top-left."""
    print("\033[2J\033[3J\033[H", end="", flush=True)


def interactive_loop(config: MazeConfig, generator: MazeGenerator) -> None:
    """Run the interactive terminal menu required by the subject."""
    show_path: bool = True
    color_index: int = 0
    regen_count: int = 0

    while True:
        clear_screen()
        print("===== A-Maze-ing =====")
        render_maze(
            grid=generator.grid,
            entry=config.entry,
            exit_pt=config.exit_pt,
            solution=generator.solution,
            show_path=show_path,
            color_index=color_index,
        )
        print("\n1. Re-generate a new maze")
        print("2. Show/Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")

        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
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
        config = parse_config(sys.argv[1])
        generator = build_and_save(config)
        interactive_loop(config, generator)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
