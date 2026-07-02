from __future__ import annotations

import argparse
from pathlib import Path

from .convert import convert_many, export_positions_csv, find_idx_files


def _expand_inputs(paths: list[Path], recursive: bool) -> list[Path]:
    idx_files: list[Path] = []
    for path in paths:
        if path.is_dir():
            idx_files.extend(find_idx_files(path, recursive=recursive))
        elif path.suffix.lower() == ".idx":
            idx_files.append(path)
        else:
            raise ValueError(f"Input is neither an .idx file nor a directory: {path}")
    return sorted(set(idx_files))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="asd2segy",
        description="Convert Parasound ASD/ACF data to SEG-Y.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="convert IDX/ACF files to SEG-Y")
    convert_parser.add_argument("inputs", nargs="+", type=Path, help=".idx files or directories")
    convert_parser.add_argument("--output-dir", required=True, type=Path, help="directory for .sgy files")
    convert_parser.add_argument("--epsg", required=True, type=int, help="projected output EPSG code")
    convert_parser.add_argument(
        "--outputs",
        nargs="+",
        choices=["envelope", "full_waveform"],
        default=["envelope"],
        help="one or more trace outputs to write",
    )
    convert_parser.add_argument("--delay-ms", type=float, default=0.0, help="trace window start")
    convert_parser.add_argument("--trace-length-ms", type=float, default=250.0, help="trace length")
    convert_parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="skip individual soundings that cannot be processed",
    )
    convert_parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="do not recurse when an input is a directory",
    )

    positions_parser = subparsers.add_parser("positions", help="export navigation positions to CSV")
    positions_parser.add_argument("inputs", nargs="+", type=Path, help=".idx files or directories")
    positions_parser.add_argument("--output", required=True, type=Path, help="CSV output path")
    positions_parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="do not recurse when an input is a directory",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    recursive = not args.no_recursive
    idx_files = _expand_inputs(args.inputs, recursive=recursive)
    if not idx_files:
        raise FileNotFoundError("No .idx files found.")

    if args.command == "convert":
        results = convert_many(
            idx_files,
            output_dir=args.output_dir,
            output_epsg=args.epsg,
            outputs=args.outputs,
            delay_ms=args.delay_ms,
            trace_length_ms=args.trace_length_ms,
            skip_errors=args.skip_errors,
        )
        for result in results:
            print(
                f"{result.output_path} "
                f"({result.output}, {result.trace_count} traces, "
                f"{result.sample_count} samples)"
            )
        return 0

    if args.command == "positions":
        output_csv = export_positions_csv(idx_files, args.output)
        print(output_csv)
        return 0

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
