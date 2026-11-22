"""Configuration file parser and validator."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MazeConfig:
    """Parsed and validated maze generation parameters."""

    width: int
    height: int
    entry: tuple[int, int]
    exit_pt: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "dfs"


def _parse_coord(raw: str, key_name: str) -> tuple[int, int]:
    """Parse a 'x,y' string into a tuple of two integers."""
    parts: list[str] = raw.split(",")
    if len(parts) != 2:
        raise ValueError(f"{key_name} must be in 'x,y' format, got '{raw}'.")
    try:
        x: int = int(parts[0].strip())
        y: int = int(parts[1].strip())
    except ValueError as err:
        raise ValueError(
            f"{key_name} coordinates must be integers, got '{raw}'."
        ) from err
    return (x, y)


def _parse_bool(raw: str, key_name: str) -> bool:
    """Parse 'True' or 'False' string into a boolean."""
    lowered: str = raw.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ValueError(f"{key_name} must be True or False, got '{raw}'.")


def parse_config(filepath: str) -> MazeConfig:
    """Read, parse, and validate a key-value maze configuration file."""
    raw_data: dict[str, str] = {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(
                        f"Syntax error on line {line_num}: (missing '=').")

                key, value = line.split("=", 1)
                key = key.strip().upper()
                value = value.strip()
                if not key or not value:
                    raise ValueError(
                        f"Syntax error on line {line_num}: empty key or value."
                        )
                raw_data[key] = value
    except OSError as err:
        raise RuntimeError(f"Could not read config file: {err}") from err

    required_keys: list[str] = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]
    for req in required_keys:
        if req not in raw_data:
            raise ValueError(f"Missing mandatory configuration key: {req}.")
    try:
        width: int = int(raw_data["WIDTH"])
        height: int = int(raw_data["HEIGHT"])
    except ValueError as err:
        raise ValueError("WIDTH and HEIGHT must be valid integers.") from err

    if width <= 0 or height <= 0:
        raise ValueError(
            "Maze dimensions (WIDTH, HEIGHT) must be positive integers.")
    if width * height < 2:
        raise ValueError("Maze must have at least 2 cells for entry and exit.")

    entry: tuple[int, int] = _parse_coord(raw_data["ENTRY"], "ENTRY")
    exit_pt: tuple[int, int] = _parse_coord(raw_data["EXIT"], "EXIT")

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError(
            f"ENTRY {entry} is outside maze bounds ({width}x{height}).")
    if not (0 <= exit_pt[0] < width and 0 <= exit_pt[1] < height):
        raise ValueError(
            f"EXIT {exit_pt} is outside maze bounds ({width}x{height}).")
    if entry == exit_pt:
        raise ValueError("ENTRY and EXIT points must be different.")

    output_file: str = raw_data["OUTPUT_FILE"]
    perfect: bool = _parse_bool(raw_data["PERFECT"], "PERFECT")

    seed: Optional[int] = None
    if "SEED" in raw_data:
        try:
            seed = int(raw_data["SEED"])
        except ValueError as err:
            raise ValueError("SEED must be an integer.") from err

    algorithm: str = raw_data.get("ALGORITHM", "dfs").lower()

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_pt=exit_pt,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm,
    )
