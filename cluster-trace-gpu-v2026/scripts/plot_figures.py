#!/usr/bin/env python3
"""Generate paper figures from aggregate and figure-input files."""

from __future__ import annotations

import argparse
from pathlib import Path

from plotters import PLOTTERS, PLOTTER_BY_NAME
from plotters import common


def parse_figure_names(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=common.DATA_ROOT,
        help="directory produced by scripts/build_aggregates.py; defaults to data/derived",
    )
    parser.add_argument("--out-dir", type=Path, default=common.OUT_DIR)
    parser.add_argument(
        "--figures",
        type=parse_figure_names,
        default=None,
        help="comma-separated figure names to plot; default plots all available figures",
    )
    parser.add_argument("--list", action="store_true", help="list available figure names and exit")
    args = parser.parse_args()

    common.configure(args.data_root, args.out_dir)
    common.OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.list:
        for plotter in PLOTTERS:
            print(f"{plotter.name}\t{plotter.output}\t{plotter.module}")
        return

    selected = args.figures
    if selected is not None:
        unknown = sorted(selected.difference(PLOTTER_BY_NAME))
        if unknown:
            raise SystemExit(f"Unknown figure name(s): {', '.join(unknown)}")

    for plotter in PLOTTERS:
        if selected is not None and plotter.name not in selected:
            continue
        if plotter.optional and not plotter.is_available():
            print(f"Skipping {plotter.name}: missing required input")
            continue
        print(f"Plotting {plotter.name} via {plotter.module}")
        plotter.plot()

    print(f"Wrote figures under {common.OUT_DIR}")


if __name__ == "__main__":
    main()
