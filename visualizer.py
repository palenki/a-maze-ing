"""ASCII terminal renderer with ANSI color support."""

Cell = tuple[int, int]
WALL_COLORS: list[str] = [
    "\033[97m",
    "\033[96m",
    "\033[93m",
    "\033[92m",
    "\033[95m",
]
RESET_COLOR = "\033[0m"
ENTRY_COLOR = "\033[92m"
EXIT_COLOR = "\033[91m"
PATH_COLOR = "\033[94m"
PATTERN_42_COLOR = "\033[93m"


def clear_screen() -> None:
    """Clear terminal screen, scrollback buffer, and move cursor home."""
    print("\033[2J\033[3J\033[H", end="", flush=True)


def render_maze(
    grid: list[list[int]],
    entry: Cell,
    exit_pt: Cell,
    pattern_cells: set[Cell],
    path_cells: set[Cell],
    show_path: bool = True,
    color_index: int = 0,
) -> None:
    """Clear screen and print the maze in ASCII art to the terminal."""
    clear_screen()
    print("===== A-Maze-ing =====")

    height: int = len(grid)
    width: int = len(grid[0])
    wall_c: str = WALL_COLORS[color_index % len(WALL_COLORS)]
    active_path: set[Cell] = path_cells if show_path else set()

    for y in range(height):
        top_line: str = ""
        for x in range(width):
            top_line += f"{wall_c}+{RESET_COLOR}"
            if grid[y][x] & 1:
                top_line += f"{wall_c}---{RESET_COLOR}"
            else:
                top_line += "   "
        top_line += f"{wall_c}+{RESET_COLOR}"
        print(top_line)

        mid_line: str = ""
        for x in range(width):
            if grid[y][x] & 8:
                mid_line += f"{wall_c}|{RESET_COLOR}"
            else:
                mid_line += " "

            curr: Cell = (x, y)
            if curr == entry:
                mid_line += f" {ENTRY_COLOR}S{RESET_COLOR} "
            elif curr == exit_pt:
                mid_line += f" {EXIT_COLOR}E{RESET_COLOR} "
            elif curr in pattern_cells:
                mid_line += f"{PATTERN_42_COLOR}###{RESET_COLOR}"
            elif curr in active_path:
                mid_line += f" {PATH_COLOR}*{RESET_COLOR} "
            else:
                mid_line += "   "

        if grid[y][width - 1] & 2:
            mid_line += f"{wall_c}|{RESET_COLOR}"
        else:
            mid_line += " "
        print(mid_line)

    bot_line: str = ""
    for x in range(width):
        bot_line += f"{wall_c}+{RESET_COLOR}"
        if grid[height - 1][x] & 4:
            bot_line += f"{wall_c}---{RESET_COLOR}"
        else:
            bot_line += "   "
    bot_line += f"{wall_c}+{RESET_COLOR}"
    print(bot_line)
