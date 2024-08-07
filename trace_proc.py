import numpy as np
from scipy import signal, interpolate
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt
import os
from datetime import datetime, timezone


import asd

from asd import ASDfile
from xml_classes import Sounding

from numpy import cos, sin


class Trace:
    
    def __init__(self) -> None:
        self.header = {'TRACE_SEQUENCE_LINE': 0, 
                             'TRACE_SEQUENCE_FILE': 0, 
                             'FieldRecord': 0, 
                             'TraceNumber': 0, 
                             'EnergySourcePoint': 0, 
                             'CDP': 0, 
                             'CDP_TRACE': 0, 
                             'TraceIdentificationCode': 0, 
                             'NSummedTraces': 0, 
                             'NStackedTraces': 0, 
                             'DataUse': 0,  # 1 - production, 2 - test
                             'offset': 0, 
                             'ReceiverGroupElevation': 0, 
                             'SourceSurfaceElevation': 0, 
                             'SourceDepth': 0, 
                             'ReceiverDatumElevation': 0, 
                             'SourceDatumElevation': 0, 
                             'SourceWaterDepth': 0, 
                             'GroupWaterDepth': 0, 
                             'ElevationScalar': 0, 
                             'SourceGroupScalar': 0, 
                             'SourceX': 0, 
                             'SourceY': 0, 
                             'GroupX': 0,  # receiver
                             'GroupY': 0,  # receiver
                             'CoordinateUnits': 0,  # 1 - lenm/ft, 2 - secarc
                             'WeatheringVelocity': 0, 
                             'SubWeatheringVelocity': 0, 
                             'SourceUpholeTime': 0, 
                             'GroupUpholeTime': 0, 
                             'SourceStaticCorrection': 0, 
                             'GroupStaticCorrection': 0, 
                             'TotalStaticApplied': 0, 
                             'LagTimeA': 0, 
                             'LagTimeB': 0, 
                             'DelayRecordingTime': 0,  # in ms
                             'MuteTimeStart': 0, 
                             'MuteTimeEND': 0, 
                             'TRACE_SAMPLE_COUNT': 0, 
                             'TRACE_SAMPLE_INTERVAL': 0, 
                             'GainType': 0, 
                             'InstrumentGainConstant': 0, 
                             'InstrumentInitialGain': 0, 
                             'Correlated': 0,  # 1 - yes, 2 - no
                             'SweepFrequencyStart': 0,  # sweep frequency at start
                             'SweepFrequencyEnd': 0,  # sweep frequency at end
                             'SweepLength': 0, 
                             'SweepType': 0,  # 1 - lin, 2 - parabol, 3 - exp, 4 - other
                             'SweepTraceTaperLengthStart': 0,  # in ms
                             'SweepTraceTaperLengthEnd': 0,  # in ms
                             'TaperType': 0,  # 1 - lin, 2 - cos, 3 - other
                             'AliasFilterFrequency': 0, 
                             'AliasFilterSlope': 0, 
                             'NotchFilterFrequency': 0, 
                             'NotchFilterSlope': 0, 
                             'LowCutFrequency': 0, 
                             'HighCutFrequency': 0, 
                             'LowCutSlope': 0, 
                             'HighCutSlope': 0, 
                             'YearDataRecorded': 0, 
                             'DayOfYear': 0, 
                             'HourOfDay': 0, 
                             'MinuteOfHour': 0, 
                             'SecondOfMinute': 0, 
                             'TimeBaseCode': 0,  # 1 - local, 2 - GMT, 3 - other
                             'TraceWeightingFactor': 0, 
                             'GeophoneGroupNumberRoll1': 0, 
                             'GeophoneGroupNumberFirstTraceOrigField': 0, 
                             'GeophoneGroupNumberLastTraceOrigField': 0, 
                             'GapSize': 0, 
                             'OverTravel': 0, 
                             'CDP_X': 0, 
                             'CDP_Y': 0, 
                             'INLINE_3D': 0, 
                             'CROSSLINE_3D': 0, 
                             'ShotPoint': 0, 
                             'ShotPointScalar': 0, 
                             'TraceValueMeasurementUnit': 0, 
                             'TransductionConstantMantissa': 0, 
                             'TransductionConstantPower': 0, 
                             'TransductionUnit': 0, 
                             'TraceIdentifier': 0, 
                             'ScalarTraceHeader': 0, 
                             'SourceType': 0, 
                             'SourceEnergyDirectionMantissa': 0, 
                             'SourceEnergyDirectionExponent': 0, 
                             'SourceMeasurementMantissa': 0, 
                             'SourceMeasurementExponent': 0, 
                             'SourceMeasurementUnit': 0}
        
        self.data = []
        self.dt = 0  # in ms
        self.acf = ''
        self.asd = ''
        
        
def resample_trace(ampls, dt, new_dt):
    num = round(dt*np.shape(ampls)[0]/new_dt)
    ampls_resampled = signal.resample(x=ampls, num=num)
    return ampls_resampled

def complex_trace(data_real, data_imag):
    complex_trace = np.ones(data_real.shape, dtype=complex)
    complex_trace.real = data_real
    complex_trace.imag = data_imag

    return complex_trace

def mag_phase(complex_trace):
    # absolute value of a complex trace - is a magnitude of a signal
    magnitude_trace = np.abs(complex_trace)
    # phase of a complex trace - is a phase of a signal at given point (in time)
    phase_trace = np.angle(complex_trace, deg=True)
    
    return magnitude_trace, phase_trace

def shift_data_to_zero_start(sample_array, data_array):
    # As it turned out, the sample start time given
    # relative to zero, i.e. sample_st/sample_dt is integer (like 198.999999 i.e. 199)
    sample_st = sample_array[0]
    sample_dt = sample_array[1] - sample_array[0]
    
    index_start = int(np.ceil(sample_st/sample_dt))
    
    sample_times = [sample_st + x*sample_dt for x in np.arange(data_array.shape[0])]
    # sample_times_shifted = [x*sample_dt for x in np.arange(data_array.shape[0] + int(sample_st/sample_dt))]
    
    func = interpolate.CubicSpline(sample_times, data_array, extrapolate=True)
    # shifted_data = func(sample_times_shifted[index_start:])
    shifted_data = func(sample_array)
    
    print(data_array)
    print(sample_times)
    
    print('______\n')
    print('Shifted data:')
    print(shifted_data)
    print(sample_array)
    
    return shifted_data, index_start
        
def shift_trace_by_heave():
    pass

def get_polar_form(z):
    # magnitude
    mag = np.abs(z)
    # phase angle in radians
    phase = np.angle(z)
    return (mag, phase)

def abs_trace(complex_trace):
    
    # abs value = complex value magnitude
    abs_value = np.sqrt(complex_trace.real**2 + complex_trace.imag**2)
    abs_value = np.abs(complex_trace)
    # phase angle, radians
    rel_angles = np.angle(complex_trace)
    
    return abs_value, rel_angles


def heave_correction(sounding: Sounding, asd_obj: ASDfile, filter=False):
    ampl_time_rel2trg = sounding.ampl_time_rel2trg  # in secs
    trg_time = sounding.trg_time  # posix seconds, absolute time
    sv_keel = asd_obj.general.sv_keel  # m/s
    

    heave = asd_obj.motion.heave  # [[m],[posix seconds]]
    heave_quality = asd_obj.motion.quality[:-1] 
    
    # Filter heave: in progress
    def filter_heave(heave, heave_quality):
        for i, qual in enumerate(heave_quality):
            if qual == 'p':
                pass
            else:
                pass
                heave.pop(i)
        
        # Filter heave: in progress

    heave_func = interpolate.CubicSpline(heave[:,1], heave[:,0], extrapolate=True)
    heave_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)
    heave_correction_secs = heave_at_ampl_time*2/sv_keel
    
    return heave_correction_secs
    

def euler_angle_rot_matrix(roll, pitch, yaw):
    # Euler Angle Rotation Matrices at event
    rot_matrix = list()

    # Transmit rotation around x-axis. Roll. R(R)
    Rx_tx = np.array([[1,                   0,                      0],
                      [0,               cos(roll),         -sin(roll)],
                      [0,               sin(roll),          cos(roll)]])

    # Transmit rotation aroung y-axis. Pitch. R(P)
    Ry_tx = np.array([[cos(pitch),           0,            sin(pitch)],
                      [0,                    1,                     0],
                      [-sin(pitch),          0,            cos(pitch)]])

    # Transmit rotation around z-axis. Yaw R(Y)
    Rz_tx = np.array([[ cos(yaw),        -sin(yaw),                 0],
                      [ sin(yaw),         cos(yaw),                 0],
                      [ 0,                    0,                    1]])              
    
    ## Compound Rotation Matrix
    rot_matrix.append(Rz_tx @ Ry_tx @ Rx_tx) ###!!! Our rotation order is: 𝑅 = 𝑅(𝑌) ⋅ 𝑅(𝑃) ⋅ 𝑅(𝑅) !!!###
    
    return rot_matrix


def attitude_integrate(sounding: Sounding, asd_obj: ASDfile):
    
    ampl_time_rel2trg = sounding.ampl_time_rel2trg  # in secs
    ampl_scan_interval = sounding.ampl_scan_interval  # in secs
    trg_time = sounding.trg_time  # posix seconds, absolute time
    sv_keel = asd_obj.general.sv_keel  # m/s
    
    # Heave part
    heave = asd_obj.motion.heave  # [[m],[posix seconds]]
    heave_quality = asd_obj.motion.quality[:-1] 
    heave_func = interpolate.interp1d(heave[:,1], heave[:,0], fill_value=0)
    heave_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)
    heave_correction_secs = heave_at_ampl_time/sv_keel*2
    
    # Roll
    roll = asd_obj.motion.roll
    roll_func = interpolate.interp1d(roll[:,1], roll[:,0], fill_value=0)
    roll_at_ampl_time = roll_func(trg_time + ampl_time_rel2trg)
    
    # Pitch
    pitch = asd_obj.motion.pitch
    pitch_func = interpolate.interp1d(pitch[:,1], pitch[:,0], fill_value=0)
    pitch_at_ampl_time = pitch_func(trg_time + ampl_time_rel2trg)
    
    # Yaw
    yaw = asd_obj.heading.heading
    yaw_func = interpolate.interp1d(yaw[:,1], yaw[:,0], fill_value=0)
    yaw_at_ampl_time = yaw_func(trg_time + ampl_time_rel2trg)
    
    rot_matrix = euler_angle_rot_matrix(roll_at_ampl_time, pitch_at_ampl_time, yaw_at_ampl_time)
    
    # print(asd_obj.installation.__dict__)
    p70_lever_arm = np.array([asd_obj.installation.tx_x, asd_obj.installation.tx_y, asd_obj.installation.tx_z]).reshape((3, 1))
    rotated_lever_arm = rot_matrix @ p70_lever_arm

    tx_z_rot = rotated_lever_arm[0,2][0]
    rot_diff = asd_obj.installation.tx_z - tx_z_rot
    
    heave_correction_secs = (heave_at_ampl_time + rot_diff)/sv_keel*2
    
    return heave_correction_secs

def get_pos_acf(idx_path):
    """ A function used for operative track creation of the
    raw Parasound P70 data

    Parameters
    ----------
    idx_path : str
        path to idx file of Parasound P70 raw data

    Returns
    -------
    list
        A list of strings with format:
        num,acf,asd,ISOdatetime,POSIXsec,lat,lon
    """

    asd_obj_list = ASDfile.create_from_idx_file(idx_path)
    
    acf_path = idx_path[:-4]
    acf_name = os.path.basename(acf_path)
    
    pos_strings = []
    
    with open(acf_path, 'rb') as f1:
        buffer = f1.read()
    
    num = 1
    
    asd_obj: ASDfile    
    for asd_obj in asd_obj_list:
        asd.parse_xml_header(asd_obj, buffer)

        base_time = asd_obj.aux_base_time  # POSIX seconds
        
        if asd_obj.position.is_valid:
            lat_lon_array = asd_obj.position.latlon
            
            for _, lat_lon in enumerate(lat_lon_array):
                
                datetime_obj = datetime.fromtimestamp(lat_lon[2], tz=timezone.utc)

                pos_string = f'{num},{acf_name},{asd_obj.name},{datetime_obj.isoformat()},{lat_lon[2]},{lat_lon[0]},{lat_lon[1]}'
                pos_strings.append(pos_string)
                num += 1
                
        else:
            datetime_obj = datetime.fromtimestamp(base_time, tz=timezone.utc)
            pos_string = f'{num},{acf_name},{asd_obj.name},{datetime_obj.isoformat()},{base_time},0.0,0.0'
            pos_strings.append(pos_string)
            num += 1
    
    return pos_strings
    
    

# функция proc_trace должна выдать массивы и заголовки, готовые для записи seg-y в segyio
def proc_trace(sounding: Sounding, asd_obj: ASDfile, delay=0, tracelen=200):  # delay and tracelen in ms
    
    ampl_time_rel2trg = sounding.ampl_time_rel2trg  # in secs
    ampl_scan_interval = sounding.ampl_scan_interval  # in secs
    delay = delay/1000  # in secs
    tracelen = tracelen/1000  # in secs
    
    # heave_correction_secs = heave_correction(sounding=sounding, asd_obj=asd_obj)
    heave_correction_secs = attitude_integrate(sounding=sounding, asd_obj=asd_obj)
    ampl_time_rel2trg_corr = ampl_time_rel2trg - heave_correction_secs

    # Real part of the complex trace is an acoustic amplitude
    # sounding.data_array[:,0] - real part of the complex trace, amplitude vallues
    # sounding.data_array[:,1] - imag part of the complex trace
    complex = complex_trace(sounding.data_array[:,0], sounding.data_array[:,1])
    envelope_data = np.abs(complex)
    
    # Original Sample Times
    sample_times = [ampl_time_rel2trg_corr + x*ampl_scan_interval for x in np.arange(envelope_data.shape[0])]
    
    # Desired Sample Times
    desired_sample_times = np.arange(delay,delay+tracelen+ampl_scan_interval,ampl_scan_interval)

    # Resample data again using desired Sample Times
    func = interpolate.CubicSpline(sample_times, envelope_data, extrapolate=False)
    
    # Data at desired Sample Times and replace numpy 'nan' values by 0
    envelope_data_at_desired = np.nan_to_num(func(desired_sample_times))
    
    return envelope_data_at_desired


def get_traces(idx_path):
    asd_obj_list = ASDfile.create_from_idx_file(idx_path)
    
    acf_path = idx_path[:-4]
    acf_name = os.path.basename(acf_path)
    
    traces = []
    
    # Load acf file into the memory
    with open(acf_path, 'rb') as f1:
        buffer = f1.read()
    

    delay = 50  # ms
    trace_len = 250  # ms

    num_of_traces = 0
    dt = 0.082
    
    
    for obj in asd_obj_list[0:5]:
        if num_of_traces > 1800:
            break
        else:
            asd.parse_xml_header(obj, buffer)
            asd.parse_bin_header(obj, buffer)
            
            
            for sounding in obj.soundings[:]:
                trace = Trace()
                
                ampls, _ = proc_trace(sounding, obj, trace, tracelen=trace_len, delay=delay)
                
                trace.dt = sounding.ampl_scan_interval*1000  # in ms
                trace.data = ampls
                
                
                traces.append(trace)
