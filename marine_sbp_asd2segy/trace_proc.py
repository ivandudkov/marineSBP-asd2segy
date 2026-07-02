import os
from datetime import datetime, timezone
from typing import Literal

import numpy as np
from scipy import interpolate, signal

from . import asd
from .asd import ASDfile
from .xml_classes import Sounding

from numpy import cos, sin


TraceOutput = Literal["envelope", "full_waveform"]


int_header = {
    "TRACE_SEQUENCE_LINE": 1,
    "TRACE_SEQUENCE_FILE": 5,
    "FieldRecord": 9,
    "TraceNumber": 13,
    "EnergySourcePoint": 17,
    "CDP": 21,
    "CDP_TRACE": 25,
    "TraceIdentificationCode": 29,
    "NSummedTraces": 31,
    "NStackedTraces": 33,
    "DataUse": 35,
    "offset": 37,
    "ReceiverGroupElevation": 41,
    "SourceSurfaceElevation": 45,
    "SourceDepth": 49,
    "ReceiverDatumElevation": 53,
    "SourceDatumElevation": 57,
    "SourceWaterDepth": 61,
    "GroupWaterDepth": 65,
    "ElevationScalar": 69,
    "SourceGroupScalar": 71,
    "SourceX": 73,
    "SourceY": 77,
    "GroupX": 81,
    "GroupY": 85,
    "CoordinateUnits": 89,
    "WeatheringVelocity": 91,
    "SubWeatheringVelocity": 93,
    "SourceUpholeTime": 95,
    "GroupUpholeTime": 97,
    "SourceStaticCorrection": 99,
    "GroupStaticCorrection": 101,
    "TotalStaticApplied": 103,
    "LagTimeA": 105,
    "LagTimeB": 107,
    "DelayRecordingTime": 109,
    "MuteTimeStart": 111,
    "MuteTimeEND": 113,
    "TRACE_SAMPLE_COUNT": 115,
    "TRACE_SAMPLE_INTERVAL": 117,
    "GainType": 119,
    "InstrumentGainConstant": 121,
    "InstrumentInitialGain": 123,
    "Correlated": 125,
    "SweepFrequencyStart": 127,
    "SweepFrequencyEnd": 129,
    "SweepLength": 131,
    "SweepType": 133,
    "SweepTraceTaperLengthStart": 135,
    "SweepTraceTaperLengthEnd": 137,
    "TaperType": 139,
    "AliasFilterFrequency": 141,
    "AliasFilterSlope": 143,
    "NotchFilterFrequency": 149,
    "NotchFilterSlope": 151,
    "LowCutFrequency": 153,
    "HighCutFrequency": 155,
    "LowCutSlope": 153,
    "HighCutSlope": 155,
    "YearDataRecorded": 157,
    "DayOfYear": 159,
    "HourOfDay": 161,
    "MinuteOfHour": 163,
    "SecondOfMinute": 165,
    "TimeBaseCode": 167,
    "TraceWeightingFactor": 169,
    "GeophoneGroupNumberRoll1": 171,
    "GeophoneGroupNumberFirstTraceOrigField": 173,
    "GeophoneGroupNumberLastTraceOrigField": 175,
    "GapSize": 177,
    "OverTravel": 179,
    "CDP_X": 181,
    "CDP_Y": 185,
    "INLINE_3D": 189,
    "CROSSLINE_3D": 193,
    "ShotPoint": 197,
    "ShotPointScalar": 201,
    "TraceValueMeasurementUnit": 203,
}


class Trace:
    """Lightweight container for one trace and its SEG-Y trace header."""

    def __init__(self) -> None:
        self.header = {key: 0 for key in int_header}
        self.data = np.array((0, 0), dtype=np.float32)
        self.dt = 0.0
        self.time = 0.0
        self.acf = ""
        self.asd = ""
        self.output: TraceOutput = "envelope"


def acf_path_from_idx(idx_path) -> str:
    idx_path = os.fspath(idx_path)
    return idx_path[:-4] if idx_path.lower().endswith(".idx") else idx_path


def resample_trace(ampls, dt, new_dt):
    num = round(dt * np.shape(ampls)[0] / new_dt)
    return signal.resample(x=ampls, num=num)


def complex_trace(data_real, data_imag):
    trace = np.ones(data_real.shape, dtype=complex)
    trace.real = data_real
    trace.imag = data_imag
    return trace


def mag_phase(data_complex):
    return np.abs(data_complex), np.angle(data_complex, deg=True)


def get_polar_form(z):
    return np.abs(z), np.angle(z)


def abs_trace(data_complex):
    return np.abs(data_complex), np.angle(data_complex)


def euler_angle_rot_matrix(roll, pitch, yaw):
    rx_tx = np.array(
        [
            [1, 0, 0],
            [0, cos(roll), -sin(roll)],
            [0, sin(roll), cos(roll)],
        ]
    )
    ry_tx = np.array(
        [
            [cos(pitch), 0, sin(pitch)],
            [0, 1, 0],
            [-sin(pitch), 0, cos(pitch)],
        ]
    )
    rz_tx = np.array(
        [
            [cos(yaw), -sin(yaw), 0],
            [sin(yaw), cos(yaw), 0],
            [0, 0, 1],
        ]
    )
    return rz_tx @ ry_tx @ rx_tx


def compute_envelope(data_complex: np.ndarray, adc_scale_factor: float) -> np.ndarray:
    """Return trace envelope in millivolts."""
    return np.abs(data_complex * adc_scale_factor * 1000.0)


def compute_full_waveform(
    data_complex: np.ndarray,
    adc_scale_factor: float,
    carrier_frequency_hz: float,
    sample_interval_s: float,
) -> np.ndarray:
    """Reconstruct a real full-waveform trace from complex baseband samples."""
    z = data_complex * adc_scale_factor * 1000.0
    sample_numbers = np.arange(z.shape[0])
    sample_rate_hz = 1.0 / sample_interval_s
    carrier = np.exp(1j * 2.0 * np.pi * carrier_frequency_hz * sample_numbers / sample_rate_hz)
    return np.real(z * carrier)


def amplitude_spectrum(data: np.ndarray, sample_interval_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Return FFT frequency axis and centered amplitude spectrum."""
    freqs = np.fft.fftfreq(len(data), d=sample_interval_s)
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(data)))
    return np.fft.fftshift(freqs), spectrum


def trace_samples(
    sounding: Sounding,
    asd_obj: ASDfile,
    output: TraceOutput = "envelope",
) -> np.ndarray:
    """Create samples for a requested trace output mode."""
    data_complex = complex_trace(sounding.data_array[:, 0], sounding.data_array[:, 1])
    if output == "envelope":
        return compute_envelope(data_complex, asd_obj.general.adc_scale_factor)
    if output == "full_waveform":
        return compute_full_waveform(
            data_complex,
            asd_obj.general.adc_scale_factor,
            sounding.slf_freq,
            sounding.ampl_scan_interval,
        )
    raise ValueError(f"Unsupported output mode: {output}")


def attitude_integrate(sounding: Sounding, asd_obj: ASDfile):
    """Compute two-way travel-time correction from attitude and TX lever arm."""
    ampl_time_rel2trg = sounding.ampl_time_rel2trg
    trg_time = sounding.trg_time
    sv_keel = asd_obj.general.sv_keel

    heave = asd_obj.motion.heave
    heave_func = interpolate.CubicSpline(heave[:, 1], heave[:, 0], extrapolate=True)
    heave_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)

    roll = asd_obj.motion.roll
    roll_func = interpolate.CubicSpline(roll[:, 1], roll[:, 0], extrapolate=True)
    roll_at_ampl_time = roll_func(trg_time + ampl_time_rel2trg)

    pitch = asd_obj.motion.pitch
    pitch_func = interpolate.CubicSpline(pitch[:, 1], pitch[:, 0], extrapolate=True)
    pitch_at_ampl_time = pitch_func(trg_time + ampl_time_rel2trg)

    yaw = asd_obj.heading.heading
    yaw_func = interpolate.CubicSpline(yaw[:, 1], yaw[:, 0], extrapolate=True)
    yaw_at_ampl_time = yaw_func(trg_time + ampl_time_rel2trg)

    rot_matrix = euler_angle_rot_matrix(roll_at_ampl_time, pitch_at_ampl_time, yaw_at_ampl_time)
    p70_lever_arm = np.array(
        [asd_obj.installation.tx_x, asd_obj.installation.tx_y, asd_obj.installation.tx_z]
    ).reshape((3, 1))
    rotated_lever_arm = rot_matrix @ p70_lever_arm

    tx_z_rot = rotated_lever_arm[2, 0]
    rot_diff = asd_obj.installation.tx_z - tx_z_rot
    heave_correction_secs = (heave_at_ampl_time + rot_diff) / sv_keel * 2.0

    return float(heave_correction_secs), rotated_lever_arm


def get_pos_acf(idx_path):
    """Return CSV lines with positions from a grouped ACF/IDX pair."""
    asd_obj_list = ASDfile.create_from_idx_file(idx_path)
    acf_path = acf_path_from_idx(idx_path)
    acf_name = os.path.basename(acf_path)

    pos_strings = []
    with open(acf_path, "rb") as f1:
        buffer = f1.read()

    num = 1
    for asd_obj in asd_obj_list:
        asd.parse_xml_header(asd_obj, buffer)
        base_time = asd_obj.aux_base_time

        if asd_obj.position.is_valid:
            for lat_lon in asd_obj.position.latlon:
                datetime_obj = datetime.fromtimestamp(lat_lon[2], tz=timezone.utc)
                pos_strings.append(
                    f"{num},{acf_name},{asd_obj.name},{datetime_obj.isoformat()},"
                    f"{lat_lon[2]},{lat_lon[0]},{lat_lon[1]}"
                )
                num += 1
        else:
            datetime_obj = datetime.fromtimestamp(base_time, tz=timezone.utc)
            pos_strings.append(
                f"{num},{acf_name},{asd_obj.name},{datetime_obj.isoformat()},"
                f"{base_time},0.0,0.0"
            )
            num += 1

    return pos_strings


def _depth_cm(asd_obj: ASDfile, first_sample_time: float) -> int:
    if not asd_obj.depths:
        return 0
    depth_obj = asd_obj.depths[1] if len(asd_obj.depths) > 1 else asd_obj.depths[0]
    if len(depth_obj.depth[:, 0]) > 1:
        depth_func = interpolate.PchipInterpolator(
            depth_obj.depth[:, 1], depth_obj.depth[:, 0], extrapolate=True
        )
        depth_m = depth_func(first_sample_time) - asd_obj.installation.tx_z
    else:
        depth_m = depth_obj.depth[0, 0] - asd_obj.installation.tx_z
    return int(np.rint(depth_m * 100.0))


def _projected_trace_position(asd_obj: ASDfile, first_sample_time: float, coord_transf, rot_la):
    if not asd_obj.position.is_valid:
        return 0.0, 0.0

    if len(asd_obj.position.latlon[:, 2]) > 1:
        lat_func = interpolate.PchipInterpolator(
            asd_obj.position.latlon[:, 2], asd_obj.position.latlon[:, 0], extrapolate=True
        )
        lon_func = interpolate.PchipInterpolator(
            asd_obj.position.latlon[:, 2], asd_obj.position.latlon[:, 1], extrapolate=True
        )
        lat = lat_func(first_sample_time)
        lon = lon_func(first_sample_time)
        x_coord, y_coord = coord_transf.transform(lon, lat)
    else:
        time = asd_obj.position.latlon[:, 2][0]
        lat = asd_obj.position.latlon[:, 0][0]
        lon = asd_obj.position.latlon[:, 1][0]
        x_coord, y_coord = coord_transf.transform(lon, lat)

        if len(asd_obj.speed_course.cog[:, 0]) > 0 and len(asd_obj.speed_course.sog[:, 0]) > 0:
            cog = asd_obj.speed_course.cog[:, 0][0]
            sog = asd_obj.speed_course.sog[:, 0][0]
            dist = sog * (first_sample_time - time)
            x_coord += np.cos(cog) * dist
            y_coord += np.sin(cog) * dist

    return x_coord + rot_la[0, 0], y_coord + rot_la[1, 0]


def proc_trace(
    trace_num,
    coord_transf,
    sounding: Sounding,
    asd_obj: ASDfile,
    delay,
    tracelen,
    output: TraceOutput = "envelope",
):
    """Build one processed trace.

    Parameters
    ----------
    delay, tracelen
        Window start and length in milliseconds.
    output
        "envelope" for magnitude trace or "full_waveform" for reconstructed
        real waveform.
    """
    trace = Trace()
    trace.output = output

    trg_time = sounding.trg_time
    ampl_time_rel2trg = sounding.ampl_time_rel2trg
    ampl_scan_interval = sounding.ampl_scan_interval
    first_sample_time = trg_time + ampl_time_rel2trg
    delay_ms = delay
    delay_s = delay / 1000.0
    tracelen_s = tracelen / 1000.0

    heave_correction_secs, rot_la = attitude_integrate(sounding=sounding, asd_obj=asd_obj)
    ampl_time_rel2trg_corr = (
        ampl_time_rel2trg
        - heave_correction_secs
        - asd_obj.installation.tx_z / asd_obj.general.sv_keel
    )

    source_data = trace_samples(sounding, asd_obj, output=output)
    sample_times = ampl_time_rel2trg_corr + np.arange(source_data.shape[0]) * ampl_scan_interval
    desired_sample_times = np.arange(
        delay_s, delay_s + tracelen_s + ampl_scan_interval, ampl_scan_interval
    )

    func = interpolate.CubicSpline(sample_times, source_data, extrapolate=False)
    trace_data = np.nan_to_num(func(desired_sample_times))

    z_offset = int(np.rint(asd_obj.installation.tx_z * 100.0))
    sounding_depth = _depth_cm(asd_obj, first_sample_time)
    x_coord_td, y_coord_td = _projected_trace_position(
        asd_obj, first_sample_time, coord_transf, rot_la
    )

    datetime_obj = datetime.fromtimestamp(first_sample_time, tz=timezone.utc)
    trace.time = ampl_time_rel2trg_corr
    trace.dt = ampl_scan_interval
    trace.data = np.float32(trace_data)

    trace.header["TRACE_SEQUENCE_LINE"] = trace_num
    trace.header["TRACE_SEQUENCE_FILE"] = trace_num
    trace.header["FieldRecord"] = 1
    trace.header["TraceNumber"] = trace_num
    trace.header["EnergySourcePoint"] = trace_num
    trace.header["TraceIdentificationCode"] = 1
    trace.header["NSummedTraces"] = 1
    trace.header["NStackedTraces"] = 1
    trace.header["DataUse"] = 1
    trace.header["ReceiverGroupElevation"] = z_offset
    trace.header["SourceDepth"] = z_offset
    trace.header["SourceWaterDepth"] = sounding_depth
    trace.header["GroupWaterDepth"] = sounding_depth
    trace.header["ElevationScalar"] = -100
    trace.header["SourceGroupScalar"] = -100

    trace.header["SourceX"] = int(np.rint(x_coord_td * 100.0))
    trace.header["SourceY"] = int(np.rint(y_coord_td * 100.0))
    trace.header["GroupX"] = int(np.rint(x_coord_td * 100.0))
    trace.header["GroupY"] = int(np.rint(y_coord_td * 100.0))
    trace.header["CoordinateUnits"] = 1

    trace.header["DelayRecordingTime"] = int(np.rint(delay_ms))
    trace.header["TRACE_SAMPLE_COUNT"] = len(desired_sample_times)
    trace.header["TRACE_SAMPLE_INTERVAL"] = int(np.rint(ampl_scan_interval * 1_000_000.0))

    trace.header["Correlated"] = 1
    trace.header["SweepFrequencyStart"] = sounding.slf_freq
    trace.header["SweepFrequencyEnd"] = sounding.slf_freq + sounding.freq_shift
    trace.header["SweepLength"] = int(np.rint(sounding.pulse_len * 1000.0))
    trace.header["SweepType"] = 4

    trace.header["YearDataRecorded"] = datetime_obj.year
    trace.header["DayOfYear"] = datetime_obj.timetuple().tm_yday
    trace.header["HourOfDay"] = datetime_obj.hour
    trace.header["MinuteOfHour"] = datetime_obj.minute
    trace.header["SecondOfMinute"] = datetime_obj.second
    trace.header["TimeBaseCode"] = 4
    trace.header["TraceValueMeasurementUnit"] = 3

    return trace


def get_traces(
    idx_path,
    coord_transf,
    delay=0,
    tracelen=250,
    output: TraceOutput = "envelope",
    skip_errors: bool = False,
):
    """Read an IDX/ACF pair and return processed traces."""
    acf_path = acf_path_from_idx(idx_path)
    asd_obj_list = ASDfile.create_from_idx_file(idx_path)
    traces = []

    with open(acf_path, "rb") as f1:
        buffer = f1.read()

    trace_num = 1
    for obj in asd_obj_list:
        asd.parse_xml_header(obj, buffer)
        asd.parse_bin_header(obj, buffer)

        for sounding in obj.soundings:
            try:
                trace = proc_trace(
                    trace_num,
                    coord_transf,
                    sounding,
                    obj,
                    tracelen=tracelen,
                    delay=delay,
                    output=output,
                )
            except Exception as exc:
                if skip_errors:
                    continue
                raise RuntimeError(
                    f"Failed to process sounding {sounding.ident_no} in {obj.name}"
                ) from exc

            trace.acf = os.path.basename(acf_path)
            trace.asd = obj.name
            traces.append(trace)
            trace_num += 1

    return traces


__all__ = [
    "Trace",
    "TraceOutput",
    "abs_trace",
    "acf_path_from_idx",
    "amplitude_spectrum",
    "attitude_integrate",
    "complex_trace",
    "compute_envelope",
    "compute_full_waveform",
    "euler_angle_rot_matrix",
    "get_polar_form",
    "get_pos_acf",
    "get_traces",
    "int_header",
    "mag_phase",
    "proc_trace",
    "resample_trace",
    "trace_samples",
]
