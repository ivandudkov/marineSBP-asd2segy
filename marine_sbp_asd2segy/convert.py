from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from .trace_proc import TraceOutput, acf_path_from_idx, get_pos_acf, get_traces, int_header


@dataclass(frozen=True)
class ConversionResult:
    """Summary of one SEG-Y conversion output."""

    input_idx: Path
    output_path: Path
    output: TraceOutput
    trace_count: int
    sample_count: int
    sample_interval_us: int


def build_transformer(output_epsg: int, input_epsg: int = 4326):
    """Create a WGS84 lon/lat to projected CRS transformer."""
    from pyproj import CRS, Transformer

    crs_wgs84 = CRS.from_epsg(input_epsg)
    crs_xy = CRS.from_epsg(output_epsg)
    return Transformer.from_crs(crs_wgs84, crs_xy, always_xy=True)


def find_idx_files(path: str | Path, recursive: bool = True) -> list[Path]:
    """Find Parasound `.idx` files under a file or directory path."""
    path = Path(path)
    if path.is_file():
        return [path] if path.suffix.lower() == ".idx" else []
    if not path.exists():
        raise FileNotFoundError(path)
    pattern = "**/*.idx" if recursive else "*.idx"
    return sorted(path.glob(pattern))


def write_segy(
    traces,
    output_path: str | Path,
    delay_ms: float = 0,
    segy_format: int = 5,
) -> Path:
    """Write processed traces to a SEG-Y file."""
    import segyio

    if not traces:
        raise ValueError("No traces to write.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sample_interval_ms = traces[0].dt * 1000.0
    samples = delay_ms + np.arange(len(traces[0].data)) * sample_interval_ms

    spec = segyio.spec()
    spec.iline = int_header["INLINE_3D"]
    spec.xline = int_header["CROSSLINE_3D"]
    spec.tracecount = len(traces)
    spec.samples = samples
    spec.ext_headers = 0
    spec.format = segy_format
    spec.endian = "big"

    with segyio.create(str(output_path), spec) as segy_file:
        for num, trace in enumerate(traces):
            segy_file.trace[num] = trace.data
            for key, byte_offset in int_header.items():
                segy_file.header[num][byte_offset] = trace.header[key]

        segy_file.bin[segyio.BinField.Interval] = traces[0].header["TRACE_SAMPLE_INTERVAL"]
        segy_file.bin[segyio.BinField.Samples] = len(traces[0].data)

    return output_path


def traces_from_idx(
    idx_path: str | Path,
    output_epsg: int,
    output: TraceOutput = "envelope",
    delay_ms: float = 0,
    trace_length_ms: float = 250,
    skip_errors: bool = False,
):
    """Read and process traces from one Parasound IDX/ACF pair."""
    transformer = build_transformer(output_epsg)
    return get_traces(
        idx_path,
        transformer,
        delay=delay_ms,
        tracelen=trace_length_ms,
        output=output,
        skip_errors=skip_errors,
    )


def convert_idx_to_segy(
    idx_path: str | Path,
    output_path: str | Path,
    output_epsg: int,
    output: TraceOutput = "envelope",
    delay_ms: float = 0,
    trace_length_ms: float = 250,
    skip_errors: bool = False,
    segy_format: int = 5,
) -> ConversionResult:
    """Convert one Parasound IDX/ACF pair to one SEG-Y file."""
    idx_path = Path(idx_path)
    traces = traces_from_idx(
        idx_path,
        output_epsg=output_epsg,
        output=output,
        delay_ms=delay_ms,
        trace_length_ms=trace_length_ms,
        skip_errors=skip_errors,
    )
    output_path = write_segy(
        traces,
        output_path,
        delay_ms=delay_ms,
        segy_format=segy_format,
    )
    return ConversionResult(
        input_idx=idx_path,
        output_path=output_path,
        output=output,
        trace_count=len(traces),
        sample_count=len(traces[0].data),
        sample_interval_us=traces[0].header["TRACE_SAMPLE_INTERVAL"],
    )


def convert_idx_outputs(
    idx_path: str | Path,
    output_dir: str | Path,
    output_epsg: int,
    outputs: Sequence[TraceOutput] = ("envelope",),
    delay_ms: float = 0,
    trace_length_ms: float = 250,
    skip_errors: bool = False,
    segy_format: int = 5,
) -> list[ConversionResult]:
    """Convert one IDX/ACF pair to one SEG-Y per requested output mode."""
    idx_path = Path(idx_path)
    output_dir = Path(output_dir)
    base_name = Path(acf_path_from_idx(idx_path)).name

    results = []
    for output in outputs:
        output_path = output_dir / f"{base_name}_{output}.sgy"
        results.append(
            convert_idx_to_segy(
                idx_path,
                output_path,
                output_epsg=output_epsg,
                output=output,
                delay_ms=delay_ms,
                trace_length_ms=trace_length_ms,
                skip_errors=skip_errors,
                segy_format=segy_format,
            )
        )
    return results


def convert_many(
    idx_paths: Iterable[str | Path],
    output_dir: str | Path,
    output_epsg: int,
    outputs: Sequence[TraceOutput] = ("envelope",),
    delay_ms: float = 0,
    trace_length_ms: float = 250,
    skip_errors: bool = False,
    segy_format: int = 5,
) -> list[ConversionResult]:
    """Convert many IDX/ACF pairs."""
    results = []
    for idx_path in idx_paths:
        results.extend(
            convert_idx_outputs(
                idx_path,
                output_dir=output_dir,
                output_epsg=output_epsg,
                outputs=outputs,
                delay_ms=delay_ms,
                trace_length_ms=trace_length_ms,
                skip_errors=skip_errors,
                segy_format=segy_format,
            )
        )
    return results


def export_positions_csv(idx_paths: Iterable[str | Path], output_csv: str | Path) -> Path:
    """Export navigation positions from one or more IDX/ACF pairs to CSV."""
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        f.write("num,acf,asd,ISOdatetime,POSIXsec,lat,lon\n")
        for idx_path in idx_paths:
            for line in get_pos_acf(idx_path):
                f.write(f"{line}\n")

    return output_csv


__all__ = [
    "ConversionResult",
    "build_transformer",
    "convert_idx_outputs",
    "convert_idx_to_segy",
    "convert_many",
    "export_positions_csv",
    "find_idx_files",
    "traces_from_idx",
    "write_segy",
]
