"""ASCII terminal renderer with ANSI color support."""

from mazegen.models import Cell, Coordinate


WALL_COLORS: List[str] = [
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


def get_path_coordinates(
    entry: tuple[int, int], solution: str
) -> set[Coordinate]:
    """Convert a path string ('NESW') into a set of visited coordinates."""
    x, y = entry
    coords: set[Coordinate] = {Coordinate(x, y)}
    deltas: dict[str, tuple[int, int]] = {
        "N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)
    }

    for step in solution:
        dx, dy = deltas[step]
        x += dx
        y += dy
        coords.add(Coordinate(x, y))
    return coords


def render_maze(
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit_pt: tuple[int, int],
    solution: str,
    show_path: bool = True,
    color_index: int = 0,
) -> None:
    """Print the maze in ASCII art to the terminal."""
    height: int = len(grid)
    width: int = len(grid[0])

    wall_c: int = WALL_COLORS[color_index % len(WALL_COLORS)]
    path_coords: set[Coordidate] = (
        get_path_coordinates(entry, solution) if show_path else set()
    )
    entry_c: tuple[int, int] = Coordinate(entry[0], entry[1])
    exit_c: tupla[int, int] = Coordinate(exit_pt[0], exit_pt[1])

    for y in range(height):
        top_line: str = ""
        for x in range(width):
            top_line += f"{wall_c}+{RESET_COLOR}"
            if grid[y][x].north:
                top_line += f"{wall_c}---{RESET_COLOR}"
            else:
                top_line += "   "
        top_line += f"{wall_c}+{RESET_COLOR}"
        print(top_line)

        mid_line: str = ""
        for x in range(width):
            if grid[y][x].west:
                mid_line += f"{wall_c}|{RESET_COLOR}"
            else:
                mid_line += " "

            curr = Coordinate(x, y)
            if curr == entry_c:
                mid_line += f" {ENTRY_COLOR}S{RESET_COLOR} "
            elif curr == exit_c:
                mid_line += f" {EXIT_COLOR}E{RESET_COLOR} "
            elif grid[y][x].is_42:
                mid_line += f"{PATTERN_42_COLOR}###{RESET_COLOR}"
            elif curr in path_coords:
                mid_line += f" {PATH_COLOR}*{RESET_COLOR} "
            else:
                mid_line += "   "

        if grid[y][width - 1].east:
            mid_line += f"{wall_c}|{RESET_COLOR}"
        else:
            mid_line += " "
        print(mid_line)

    bot_line: str = ""
    for x in range(width):
        bot_line += f"{wall_c}+{RESET_COLOR}"
        if grid[height - 1][x].south:
            bot_line += f"{wall_c}---{RESET_COLOR}"
        else:
            bot_line += "   "
    bot_line += f"{wall_c}+{RESET_COLOR}"
    print(bot_line)
