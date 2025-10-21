import numpy as np

import matplotlib.pyplot as plt
import segyio

"""
Visualize a seismic profile from a SEG-Y (.sgy) file using matplotlib and segyio.

Usage:
  python visualize_segy.py path/to/line.sgy --kind both --clip 99.5 --stride 2 --wiggle-scale 0.6 --outfile line.png

Why certain choices:
- Global percentile clipping yields stable contrast across traces.
- Global normalization for wiggles avoids trace-to-trace visual bias.
- `ignore_geometry=True` ensures reading works even if geometry is absent/invalid.

Requirements:
  pip install segyio matplotlib numpy
"""

import argparse
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
import segyio



class MySpec(object):
    def __init__(self):
        self.iline = 189  # default value for segyio
        self.xline = 193  # default value for segyio
        self.tracecount = 0
        self.samples = []  # sample times, a list
        self.ext_headers = 0
        self.format = 5  # 4-byte IEEE float
        self.endian = 'big'

def plot_rawtraces(raw_traces):
    clip = 1e+3
    vmin, vmax = -clip, clip

    # Figure
    figsize=(20, 20)
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor='w', edgecolor='k',
                        squeeze=False,
                        sharex=True)
    axs = axs.ravel()
    im = axs[0].imshow(raw_traces.T, cmap=plt.cm.seismic, vmin=vmin, vmax=vmax)
    plt.show()


path = r'C:\YandexDisk\MyProjects\InspectingP70Data\P70_data\PS3SLF_2022-06-01T112446Z_02157600_-0_W1_SLF2109171103_LL_env.sgy'



def load_segy(path: Path) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Load traces from a SEG-Y file.

    Returns:
        data: float32 array shaped (n_samples, n_traces)
        t_s: 1D time axis in seconds (length n_samples)
        dt_s: sample interval in seconds
    """
    with segyio.open(str(path), ignore_geometry=True, strict=False, endian='big') as f:
        traces = segyio.collect(f.trace[:])  # (n_traces, n_samples)
        data = traces.T.astype(np.float32, copy=False)
        try:
            dt_us = int(f.bin[segyio.BinField.Interval])  # microseconds
        except Exception:
            dt_us = 1000  # fallback 1 ms
        if dt_us <= 0:
            dt_us = 1000
        dt_s = dt_us / 1_000_000.0
        n_samples = data.shape[0]
        t_s = np.arange(n_samples, dtype=np.float32) * dt_s
    return data, t_s, dt_s

def symmetric_clip(data: np.ndarray, clip_percentile: float) -> Tuple[float, float]:
    """
    Symmetric clipping around zero based on |amplitude| percentile.
    """
    p = np.nanpercentile(np.abs(data), clip_percentile)
    if p == 0 or not np.isfinite(p):
        p = 1.0
    return -p, p


def plot_image(
    ax: plt.Axes,
    data: np.ndarray,
    t_s: np.ndarray,
    vmin: Optional[float],
    vmax: Optional[float],
) -> None:
    """
    Render amplitude image with time increasing downward.
    """
    n_samples, n_traces = data.shape
    extent = [0, n_traces - 1, t_s[-1], t_s[0]]
    im = ax.imshow(
        data,
        aspect="auto",
        extent=extent,
        vmin=vmin,
        vmax=vmax,
        cmap="gray",
        interpolation="nearest",
        origin="upper",
    )
    ax.set_xlabel("Trace #")
    ax.set_ylabel("Time (s)")
    ax.invert_yaxis()
    cbar = plt.colorbar(im, ax=ax, pad=0.01)
    cbar.set_label("Amplitude")


def plot_wiggle(
    ax: plt.Axes,
    data: np.ndarray,
    t_s: np.ndarray,
    stride: int = 1,
    wiggle_scale: float = 0.6,
    linewidth: float = 0.5,
    fill_positive: bool = True,
) -> None:
    """
    Draw a classical wiggle (variable-area) plot.

    Why:
    - Uses global p99 scale for consistent visual amplitude across the section.
    - Stride reduces overdraw for dense lines.
    """
    n_samples, n_traces = data.shape
    p99 = np.nanpercentile(np.abs(data), 99.0)
    if p99 == 0 or not np.isfinite(p99):
        p99 = 1.0
    scale = wiggle_scale / p99

    for j in range(0, n_traces, max(1, stride)):
        trace = data[:, j]
        x0 = j
        x = x0 + trace * scale
        ax.plot(x, t_s, linewidth=linewidth)
        if fill_positive:
            ax.fill_betweenx(t_s, x0, x, where=(x >= x0), alpha=0.5, linewidth=0.0)
    ax.set_xlabel("Trace #")
    ax.set_ylabel("Time (s)")
    ax.invert_yaxis()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Visualize SEG-Y seismic profile.")
    p.add_argument("input", type=Path, help="Path to .sgy file")
    p.add_argument(
        "--kind",
        choices=["image", "wiggle", "both"],
        default="image",
        help="Visualization type",
    )
    p.add_argument(
        "--clip",
        type=float,
        default=99.5,
        help="Symmetric clip percentile for image (e.g., 99.0..99.9).",
    )
    p.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Plot every Nth trace for wiggles.",
    )
    p.add_argument(
        "--wiggle-scale",
        type=float,
        default=0.6,
        help="Horizontal scale factor for wiggles (relative).",
    )
    p.add_argument(
        "--linewidth",
        type=float,
        default=0.5,
        help="Wiggle line width.",
    )
    p.add_argument(
        "--no-fill",
        action="store_true",
        help="Disable variable-area fill for positive lobes.",
    )
    p.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Figure DPI for saving.",
    )
    p.add_argument(
        "--title",
        type=str,
        default=None,
        help="Optional figure title.",
    )
    p.add_argument(
        "--outfile",
        type=Path,
        default=None,
        help="If set, save the figure to this path instead of showing.",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Input not found: {args.input}")

    data, t_s, _ = load_segy(args.input)

    # Compute symmetric vmin/vmax for image visualization.
    vmin = vmax = None
    if args.kind in {"image", "both"}:
        vmin, vmax = symmetric_clip(data, args.clip)

    fig = plt.figure(figsize=(10, 6), dpi=args.dpi)
    ax = fig.add_subplot(111)

    if args.kind == "image":
        plot_image(ax, data, t_s, vmin, vmax)
    elif args.kind == "wiggle":
        plot_wiggle(
            ax,
            data,
            t_s,
            stride=max(1, args.stride),
            wiggle_scale=args.wiggle_scale,
            linewidth=args.linewidth,
            fill_positive=not args.no_fill,
        )
    else:  # both
        plot_image(ax, data, t_s, vmin, vmax)
        plot_wiggle(
            ax,
            data,
            t_s,
            stride=max(1, args.stride),
            wiggle_scale=args.wiggle_scale,
            linewidth=args.linewidth,
            fill_positive=not args.no_fill,
        )
        ax.set_title(args.title or f"{args.input.name} — image + wiggle")
        plt.tight_layout()
        if args.outfile is not None:
            fig.savefig(args.outfile, dpi=args.dpi, bbox_inches="tight")
            return
        plt.show()
        return

    ax.set_title(args.title or args.input.name)
    plt.tight_layout()
    if args.outfile is not None:
        fig.savefig(args.outfile, dpi=args.dpi, bbox_inches="tight")
    else:
        plt.show()


main()

# if __name__ == "test_segy_open":
#     main()
