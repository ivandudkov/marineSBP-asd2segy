import numpy as np
import segyio

from marine_sbp_asd2segy.convert import write_segy
from marine_sbp_asd2segy.trace_proc import (
    Trace,
    amplitude_spectrum,
    compute_envelope,
    compute_full_waveform,
)


def test_compute_envelope_returns_magnitude_in_millivolts():
    data = np.array([3 + 4j, 5 + 12j], dtype=np.complex128)

    envelope = compute_envelope(data, adc_scale_factor=0.001)

    np.testing.assert_allclose(envelope, np.array([5.0, 13.0]))


def test_compute_full_waveform_zero_carrier_matches_real_part():
    data = np.array([1 + 2j, 3 + 4j], dtype=np.complex128)

    waveform = compute_full_waveform(
        data,
        adc_scale_factor=0.001,
        carrier_frequency_hz=0.0,
        sample_interval_s=0.001,
    )

    np.testing.assert_allclose(waveform, np.array([1.0, 3.0]))


def test_amplitude_spectrum_returns_matching_axes():
    data = np.ones(8, dtype=np.float32)

    freq_hz, amplitude = amplitude_spectrum(data, sample_interval_s=0.001)

    assert freq_hz.shape == amplitude.shape == data.shape


def test_write_segy_smoke(tmp_path):
    traces = []
    for index in range(2):
        trace = Trace()
        trace.data = np.arange(4, dtype=np.float32) + index
        trace.dt = 0.001
        trace.header["TRACE_SEQUENCE_LINE"] = index + 1
        trace.header["TRACE_SEQUENCE_FILE"] = index + 1
        trace.header["TraceNumber"] = index + 1
        trace.header["TRACE_SAMPLE_COUNT"] = 4
        trace.header["TRACE_SAMPLE_INTERVAL"] = 1000
        traces.append(trace)

    output_path = write_segy(traces, tmp_path / "smoke.sgy")

    with segyio.open(str(output_path), ignore_geometry=True, strict=False, endian="big") as segy_file:
        assert len(segy_file.trace) == 2
        assert len(segy_file.samples) == 4
        assert int(segy_file.bin[segyio.BinField.Interval]) == 1000
