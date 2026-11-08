"""Configuration file loader and validador"""


from dataclasses import dataclass
from typing import Optional
from mazegen.models import Point


@dataclass(frozen=True)
class Config:
	"""Parsed and validated maze generation parameters."""
	width: int
	height: int
	entry: Point
	exit_pt: Point
	output_file: str
	perfect: bool
	seed: Optional[int]


def parse_config(filepath: str) -> Config:
	raw_data: dict[str, str] = {}

	with open(filepath, "r", encoding="utf-8") as file:
		for line_num, line in enumerate(file, 1)
			line = line.strip()
			if not line or line.startswith("#")
				continue

			if "=" not in line:
				raise ValueError(f"Line {line_num}: Invalid line format (missing '=')")
			key, value = line.split("=", 1)
			raw_data[key.strip()] = value.strip()

	mandatory_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
	missing = mandatory_keys - raw_data.keys()
	if missing:
		raise ValueError(f"Missing mandatory configuration keys: {', '.join(missing)}")
	try:
        width = int(raw_data["WIDTH"])
        height = int(raw_data["HEIGHT"])

        entry_parts = [int(i) for i in raw_data["ENTRY"].split(",")]
        exit_parts = [int(i) for i in raw_data["EXIT"].split(",")]

        if len(entry_parts) != 2 or len(exit_parts) != 2:
            raise ValueError("ENTRY and EXIT must be in 'x,y' format.")

        entry = Point(entry_parts[0], entry_parts[1])
        exit_pt = Point(exit_parts[0], exit_parts[1])

        output_file = raw_data["OUTPUT_FILE"]
        perfect = raw_data["PERFECT"].lower() in ("true", "1", "yes")

        seed: Optional[int] = None
        if "SEED" in raw_data:
            seed = int(raw_data["SEED"])

    except ValueError as err:
        raise ValueError(f"Error parsing numerical configuration values: {err}") from err
	# Business rules validation
    if width <= 0 or height <= 0:
        raise ValueError("Maze dimensions (WIDTH, HEIGHT) must be positive integers.")
    if not (0 <= entry.x < width and 0 <= entry.y < height):
        raise ValueError(f"ENTRY {entry} is outside maze bounds ({width}x{height}).")
    if not (0 <= exit_pt.x < width and 0 <= exit_pt.y < height):
        raise ValueError(f"EXIT {exit_pt} is outside maze bounds ({width}x{height}).")
    if entry == exit_pt:
        raise ValueError("ENTRY and EXIT points must be different.")

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit_pt=exit_pt,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )
