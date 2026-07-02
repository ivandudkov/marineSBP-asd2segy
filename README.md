# marineSBP-asd2segy

Convert Parasound P70 grouped ASD/ACF sub-bottom profiler data to SEG-Y.

The package reads a Parasound `.asd.acf.idx` index file together with the
matching `.asd.acf` binary file, parses XML and binary sounding blocks, builds
georeferenced traces, and writes conventional SEG-Y files with `segyio`.

## Outputs

Two trace outputs are supported:

- `envelope`: magnitude of the complex I/Q trace, exported in millivolts.
- `full_waveform`: reconstructed real waveform from the complex baseband samples
  and the sounding carrier frequency.

Both outputs can be produced from the same input file in one workflow.

## Installation

```bash
python -m pip install -e .
```

For notebooks and plotting examples:

```bash
python -m pip install -e ".[examples]"
```

For local development checks:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Input Layout

For an index file such as:

```text
data/PS3SLF_2024-07-07T174231Z_07793648.asd.acf.idx
```

the matching ACF file is expected at:

```text
data/PS3SLF_2024-07-07T174231Z_07793648.asd.acf
```

The converter also needs an output projected CRS EPSG code, for example UTM zone
34N is `32634`.

## Python API

```python
from marine_sbp_asd2segy import convert_idx_outputs

results = convert_idx_outputs(
    "data/line.asd.acf.idx",
    output_dir="outputs",
    output_epsg=32634,
    outputs=("envelope", "full_waveform"),
    delay_ms=0,
    trace_length_ms=250,
)

for result in results:
    print(result.output_path, result.trace_count)
```

Batch conversion:

```python
from marine_sbp_asd2segy import convert_many, find_idx_files

idx_files = find_idx_files("data/raw", recursive=True)
convert_many(
    idx_files,
    output_dir="outputs",
    output_epsg=32634,
    outputs=("envelope",),
)
```

Export navigation positions:

```python
from marine_sbp_asd2segy import export_positions_csv, find_idx_files

idx_files = find_idx_files("data/raw")
export_positions_csv(idx_files, "outputs/navigation.csv")
```

Low-level trace processing and spectrum inspection:

```python
from marine_sbp_asd2segy import amplitude_spectrum, traces_from_idx

traces = traces_from_idx(
    "data/line.asd.acf.idx",
    output_epsg=32634,
    output="full_waveform",
)
freq_hz, amplitude = amplitude_spectrum(traces[0].data, traces[0].dt)
```

## CLI

Convert one file to both outputs:

```bash
asd2segy convert data/line.asd.acf.idx \
  --output-dir outputs \
  --epsg 32634 \
  --outputs envelope full_waveform \
  --delay-ms 0 \
  --trace-length-ms 250
```

Convert all `.idx` files in a directory:

```bash
asd2segy convert data/raw --output-dir outputs --epsg 32634 --outputs envelope
```

Export positions:

```bash
asd2segy positions data/raw --output outputs/navigation.csv
```

## Notebooks

- `notebooks/01_convert_acf_to_segy.ipynb`: programmatic conversion examples.
- `notebooks/02_inspect_outputs_and_spectrum.ipynb`: SEG-Y preview and spectrum
  inspection.

The repository does not include raw Parasound data. Edit the path variables in
the first cells of the notebooks before running them.

## Notes and Limitations

- The current parser targets grouped Parasound `.asd.acf` files with `.idx`
  sidecar files.
- Coordinates are read from WGS84 positions and written as projected coordinates
  scaled by `SourceGroupScalar = -100`.
- SEG-Y sample format defaults to IEEE 4-byte float (`format=5`).
- If `skip_errors=True` or `--skip-errors` is used, individual soundings that
  fail processing are skipped.

## License

MIT License. See `LICENSE`.
