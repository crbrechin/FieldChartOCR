"""
Utility for synthesizing bar-chart table data.

The script emits CSV files that mirror the structure of the sample tables in
`output_files/`, providing both single-series and grouped-series variants.
Each generated CSV is accompanied by a manifest entry stored in
`synthetic_bar_manifest.json` inside the chosen output directory.

Example:
    python generate_synthetic_bar_tables.py --output-dir output_files/synthetic/bar \
        --single-count 15 --grouped-count 12 --seed 123
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


# Pools of labels to keep charts varied and realistic.
SINGLE_SERIES_CATEGORY_POOLS: Sequence[Sequence[str]] = (
    ("Lion", "Zebra", "Bear", "Tiger", "Snake", "Giraffe", "Hippo"),
    ("Solar", "Wind", "Hydro", "Nuclear", "Geothermal", "Biomass"),
    ("Q1", "Q2", "Q3", "Q4"),
    ("Compressor", "Generator", "Pump", "Valve", "Sensor", "Actuator"),
    ("North", "South", "East", "West", "Central"),
    ("Prototype A", "Prototype B", "Prototype C", "Prototype D"),
    ("Apple", "Banana", "Cherry", "Date", "Fig"),
    ("Copper", "Iron", "Gold", "Silver", "Platinum"),
    ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"),
    ("Jazz", "Rock", "Pop", "Classical", "Hip-Hop"),
    ("Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"),
    ("Python", "Java", "C++", "JavaScript", "Go", "Rust"),
    ("SUV", "Sedan", "Truck", "Coupe", "Convertible"),
    ("Red", "Green", "Blue", "Yellow", "Black", "White"),
    ("Dog", "Cat", "Rabbit", "Horse", "Sheep", "Cow"),
    ("Coffee", "Tea", "Juice", "Water", "Milk", "Soda"),
    ("Rectangle", "Circle", "Triangle", "Square", "Pentagon", "Hexagon"),
    ("Jazz", "Blues", "Reggae", "Funk", "Soul", "Country"),
    ("Chef", "Doctor", "Lawyer", "Engineer", "Artist"),
    ("Physics", "Chemistry", "Biology", "Math", "Geology", "Astronomy"),
    ("Bread", "Rice", "Pasta", "Potato", "Corn", "Quinoa"),
    ("Star", "Planet", "Comet", "Asteroid", "Nebula", "Galaxy"),
    ("Winter", "Spring", "Summer", "Autumn"),
    ("Guitar", "Piano", "Drums", "Violin", "Trumpet", "Cello"),
    ("Oak", "Pine", "Birch", "Maple", "Spruce", "Cedar"),
    ("Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"),
    ("Circle", "Ellipse", "Arc", "Sector", "Chord"),
    ("Bus", "Train", "Plane", "Boat", "Bicycle", "Car"),
    ("Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn"),
    ("Server", "Client", "Database", "Router", "Switch"),
)

GROUP_PRIMARY_LABELS: Sequence[Sequence[str]] = (
    ("Green", "Blue", "Yellow", "Red", "Purple"),
    ("Project A", "Project B", "Project C", "Project D"),
    ("Team Alpha", "Team Beta", "Team Gamma", "Team Delta"),
    ("Year 1", "Year 2", "Year 3", "Year 4"),
    ("Summer", "Autumn", "Winter", "Spring"),
    ("Europe", "Asia", "Africa", "America"),
    ("Bronze", "Silver", "Gold", "Platinum"),
    ("Leader", "Member", "Advisor", "Intern"),
    ("Vanilla", "Chocolate", "Strawberry", "Mint", "Coffee"),
    ("CPU", "GPU", "RAM", "SSD", "HDD"),
    ("Morning", "Afternoon", "Evening", "Night"),
    ("Section 1", "Section 2", "Section 3", "Section 4"),
    ("Windows", "Mac", "Linux", "Unix"),
    ("Dog", "Cat", "Horse", "Bird"),
    ("Easy", "Medium", "Hard", "Expert"),
    ("Sales", "Marketing", "Engineering", "HR"),
    ("Primary", "Secondary", "Tertiary", "Quaternary"),
    ("Student", "Teacher", "Principal", "Counselor"),
    ("A", "B", "C", "D", "E", "F"),
    ("Sakura", "Rose", "Tulip", "Lily"),
    ("Song 1", "Song 2", "Song 3", "Song 4", "Song 5"),
    ("Batch 1", "Batch 2", "Batch 3"),
    ("Alpha 1", "Alpha 2", "Beta 1", "Beta 2"),
    ("Product X", "Product Y", "Product Z"),
    ("East", "West", "North", "South"),
    ("Freshman", "Sophomore", "Junior", "Senior"),
    ("Admin", "User", "Guest", "Moderator"),
    ("Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"),
)

GROUP_SECONDARY_LABELS: Sequence[Sequence[str]] = (
    ("Preschool", "Primary", "Secondary"),
    ("On-Time", "Delayed", "Critical"),
    ("Low", "Medium", "High"),
    ("Week 1", "Week 2", "Week 3", "Week 4"),
    ("Yes", "No", "Maybe"),
    ("Standard", "Premium", "Deluxe"),
    ("1st", "2nd", "3rd"),
    ("Small", "Medium", "Large", "Extra Large"),
    ("Gold", "Silver", "Bronze"),
    ("Less", "Equal", "More"),
    ("Blue", "Red", "Green", "Yellow"),
    ("Pass", "Fail", "Incomplete"),
    ("Short", "Medium", "Tall"),
    ("Circle", "Square", "Triangle"),
    ("Spring", "Summer", "Autumn", "Winter"),
    ("Young", "Adult", "Senior"),
    ("Single", "Double", "Triple"),
    ("Morning", "Noon", "Night"),
    ("Home", "Away", "Neutral"),
    ("Odd", "Even", "Prime"),
    ("Mild", "Spicy", "Hot"),
    ("Economy", "Business", "First"),
    ("A", "B", "C", "D"),
    ("East", "West", "Central"),
    ("Red", "Green", "Blue"),
    ("Hot", "Warm", "Cool", "Cold"),
    ("Sunny", "Cloudy", "Rainy", "Snowy"),
    ("Alpha", "Beta", "Gamma"),
)



@dataclass
class TableSpec:
    table_type: str
    header: Tuple[str, ...]
    source_file: str
    primary_label: str | None = None
    secondary_label: str | None = None
    notes: str | None = None


def random_from_pool(pool: Sequence[Sequence[str]]) -> Sequence[str]:
    """Return a random list from a pool."""
    return random.choice(pool)


def choose_labels(pool: Sequence[Sequence[str]], min_len: int, max_len: int) -> List[str]:
    """Choose a subset of labels from a pool while preserving ordering."""
    labels = list(random_from_pool(pool))
    k = random.randint(min(min_len, len(labels)), min(max_len, len(labels)))
    return labels[:k]


def gen_single_series() -> Tuple[TableSpec, List[Tuple[str, int]]]:
    labels = choose_labels(SINGLE_SERIES_CATEGORY_POOLS, 4, 6)
    header = ("Category", "Value")
    rows = []
    for label in labels:
        base = random.randint(10, 70)
        noise = random.randint(-5, 8)
        value = max(1, base + noise)
        rows.append((label, value))

    spec = TableSpec(
        table_type="single_series",
        header=header,
        source_file="sample_table_001.csv",
        notes="Synthesized single-series bar chart table.",
    )
    return spec, rows


def gen_grouped_series() -> Tuple[TableSpec, List[Tuple[str, str, int]]]:
    primary_labels = choose_labels(GROUP_PRIMARY_LABELS, 3, 5)
    secondary_labels = choose_labels(GROUP_SECONDARY_LABELS, 3, 4)
    header = ("Group", "Subgroup", "Value")
    rows: List[Tuple[str, str, int]] = []

    for primary in primary_labels:
        base = random.randint(5, 9)
        share_total = random.uniform(12.0, 25.0)
        weights = [abs(random.gauss(1.0, 0.4)) for _ in secondary_labels]
        weight_sum = sum(weights) or 1.0
        normalized = [w / weight_sum for w in weights]

        for secondary, weight in zip(secondary_labels, normalized):
            value = max(1, int(round(base + share_total * weight + random.uniform(-1.5, 1.5))))
            rows.append((primary, secondary, value))

    spec = TableSpec(
        table_type="grouped_series",
        header=header,
        source_file="sample_table_002.csv",
        primary_label="/".join(primary_labels),
        secondary_label="/".join(secondary_labels),
        notes="Synthesized grouped bar chart table.",
    )
    return spec, rows


def write_csv(path: Path, header: Sequence[str], rows: Sequence[Sequence[int | str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic bar-chart CSV tables.")
    parser.add_argument("--output-dir", type=Path, default=Path("output_files/synthetic/bar"))
    parser.add_argument("--single-count", type=int, default=10, help="Number of single-series tables to generate.")
    parser.add_argument("--grouped-count", type=int, default=10, help="Number of grouped-series tables to generate.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducibility.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "synthetic_bar_manifest.json"
    manifest: Dict[str, Dict[str, object]] = {}

    counter = 1

    for _ in range(args.single_count):
        spec, rows = gen_single_series()
        filename = f"bar_single_{counter:03d}.csv"
        counter += 1
        csv_path = output_dir / filename
        write_csv(csv_path, spec.header, rows)
        manifest[filename] = asdict(spec)

    for _ in range(args.grouped_count):
        spec, rows = gen_grouped_series()
        filename = f"bar_grouped_{counter:03d}.csv"
        counter += 1
        csv_path = output_dir / filename
        write_csv(csv_path, spec.header, rows)
        manifest[filename] = asdict(spec)

    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"Generated {args.single_count + args.grouped_count} tables in {output_dir}")
    print(f"Manifest saved to {manifest_path}")


if __name__ == "__main__":
    main()

