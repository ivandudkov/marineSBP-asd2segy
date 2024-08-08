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


int_header = {'TRACE_SEQUENCE_LINE': 1, 
                             'TRACE_SEQUENCE_FILE': 5, 
                             'FieldRecord': 9, 
                             'TraceNumber': 13, 
                             'EnergySourcePoint': 17, 
                             'CDP': 21, 
                             'CDP_TRACE': 25, 
                             'TraceIdentificationCode': 29, 
                             'NSummedTraces': 31, 
                             'NStackedTraces': 33, 
                             'DataUse': 35,  # 1 - production, 2 - test
                             'offset': 37, 
                             'ReceiverGroupElevation': 41, 
                             'SourceSurfaceElevation': 45, 
                             'SourceDepth': 49, 
                             'ReceiverDatumElevation': 53, 
                             'SourceDatumElevation': 57, 
                             'SourceWaterDepth': 61, 
                             'GroupWaterDepth': 65, 
                             'ElevationScalar': 69, 
                             'SourceGroupScalar': 71, 
                             'SourceX': 73, 
                             'SourceY': 77, 
                             'GroupX': 81,  # receiver
                             'GroupY': 85,  # receiver
                             'CoordinateUnits': 89,  # 1 - lenm/ft, 2 - secarc
                             'WeatheringVelocity': 91, 
                             'SubWeatheringVelocity': 93, 
                             'SourceUpholeTime': 95, 
                             'GroupUpholeTime': 97, 
                             'SourceStaticCorrection': 99, 
                             'GroupStaticCorrection': 101, 
                             'TotalStaticApplied': 103, 
                             'LagTimeA': 105, 
                             'LagTimeB': 107, 
                             'DelayRecordingTime': 109,  # in ms
                             'MuteTimeStart': 111, 
                             'MuteTimeEND': 113, 
                             'TRACE_SAMPLE_COUNT': 115, 
                             'TRACE_SAMPLE_INTERVAL': 117, 
                             'GainType': 119, 
                             'InstrumentGainConstant': 121, 
                             'InstrumentInitialGain': 123, 
                             'Correlated': 125,  # 1 - yes, 2 - no
                             'SweepFrequencyStart': 127,  # sweep frequency at start
                             'SweepFrequencyEnd': 129,  # sweep frequency at end
                             'SweepLength': 131,  # in ms 
                             'SweepType': 133,  # 1 - lin, 2 - parabol, 3 - exp, 4 - other
                             'SweepTraceTaperLengthStart': 135,  # in ms
                             'SweepTraceTaperLengthEnd': 137,  # in ms
                             'TaperType': 139,  # 1 - lin, 2 - cos, 3 - other
                             'AliasFilterFrequency': 141, 
                             'AliasFilterSlope': 143, 
                             'NotchFilterFrequency': 149, 
                             'NotchFilterSlope': 151, 
                             'LowCutFrequency': 153, 
                             'HighCutFrequency': 155, 
                             'LowCutSlope': 153, 
                             'HighCutSlope': 155, 
                             'YearDataRecorded': 157, 
                             'DayOfYear': 159, 
                             'HourOfDay': 161, 
                             'MinuteOfHour': 163, 
                             'SecondOfMinute': 165, 
                             'TimeBaseCode': 167,  # 1 - local, 2 - GMT, 3 - other, 4 - UTC
                             'TraceWeightingFactor': 169, 
                             'GeophoneGroupNumberRoll1': 171, 
                             'GeophoneGroupNumberFirstTraceOrigField': 173, 
                             'GeophoneGroupNumberLastTraceOrigField': 175, 
                             'GapSize': 177, 
                             'OverTravel': 179, 
                             'CDP_X': 181, 
                             'CDP_Y': 185, 
                             'INLINE_3D': 189, 
                             'CROSSLINE_3D': 193, 
                             'ShotPoint': 197, 
                             'ShotPointScalar': 201, 
                             'TraceValueMeasurementUnit': 203}


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
                             'TimeBaseCode': 0,  # 1 - local, 2 - GMT, 3 - other, 4 - UTC
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
                             'TraceValueMeasurementUnit': 0}
        
        self.data = []
        self.dt = 0  # in ms
        self.time = 0  # POSIX time tag
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
    trg_time = sounding.trg_time  # posix seconds, absolute time
    sv_keel = asd_obj.general.sv_keel  # m/s
    
    # Heave part
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
    
    return heave_correction_secs, rotated_lever_arm

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
def proc_trace(trace_num, coord_transf, sounding: Sounding, asd_obj: ASDfile, delay, tracelen):  # delay and tracelen in ms
    
    trace = Trace()
    
    trg_time = sounding.trg_time
    
    ampl_time_rel2trg = sounding.ampl_time_rel2trg  # in secs
    ampl_scan_interval = sounding.ampl_scan_interval  # in secs
    adc_scale_factor = asd_obj.general.adc_scale_factor  # used to convert values to [V]olts
    first_sample_time = trg_time + ampl_time_rel2trg
    
    delay = delay/1000  # in secs
    tracelen = tracelen/1000  # in secs
    
    # Heave correction and equipment z offset correction
    heave_correction_secs, rot_la = attitude_integrate(sounding=sounding, asd_obj=asd_obj)

    ampl_time_rel2trg_corr = ampl_time_rel2trg - heave_correction_secs - asd_obj.installation.tx_z/asd_obj.general.sv_keel

    # Real part of the complex trace is an acoustic amplitude
    # sounding.data_array[:,0] - real part of the complex trace
    # sounding.data_array[:,1] - imag part of the complex trace
    complex = complex_trace(sounding.data_array[:,0], sounding.data_array[:,1])
    envelope_data = np.abs(complex*adc_scale_factor*1000)  # convert counts to [mV] (milli-volts)
    
    # Original Sample Times
    sample_times = [ampl_time_rel2trg_corr + x*ampl_scan_interval for x in np.arange(envelope_data.shape[0])]
    
    # Desired Sample Times
    desired_sample_times = np.arange(delay,delay+tracelen+ampl_scan_interval,ampl_scan_interval)

    # Make a func representing data
    func = interpolate.CubicSpline(sample_times, envelope_data, extrapolate=False)
    
    # Catch data at desired Sample Times and replace numpy 'nan' values by 0
    envelope_data_at_desired = np.nan_to_num(func(desired_sample_times))
    
    
    z_offset = int(asd_obj.installation.tx_z*100)
    depth_obj = asd_obj.depths[1]
    
    if len(depth_obj.depth[:,0]) > 1:
        depth_func = interpolate.PchipInterpolator(depth_obj.depth[:,1], depth_obj.depth[:,0], extrapolate=True)
        sounding_depth = int((depth_func(first_sample_time) - asd_obj.installation.tx_z)*100)
    else:
        sounding_depth = int((depth_obj.depth[0,0]- asd_obj.installation.tx_z)*100)
    
    if asd_obj.position.is_valid:
        if len(asd_obj.position.latlon[:,2]) > 1:
            lat_func = interpolate.PchipInterpolator(asd_obj.position.latlon[:,2], asd_obj.position.latlon[:,0], extrapolate=True)
            lon_func = interpolate.PchipInterpolator(asd_obj.position.latlon[:,2], asd_obj.position.latlon[:,1], extrapolate=True)
            
            lat = lat_func(first_sample_time)
            lon = lon_func(first_sample_time)
            
            x_coord, y_coord = coord_transf.transform(lon, lat)

        else:
            time = asd_obj.position.latlon[:,2][0]
            lat = asd_obj.position.latlon[:,0][0]
            lon = asd_obj.position.latlon[:,1][0]
            
            cog = asd_obj.speed_course.cog[:,0][0]
            sog = asd_obj.speed_course.sog[:,0][0]
            
            time_diff = (first_sample_time) - time
            dist = sog*time_diff
            
            x = np.cos(cog)*dist
            y = np.sin(cog)*dist
                
            x_coord, y_coord = coord_transf.transform(lon, lat)
            
            x_coord = x_coord + x
            y_coord = y_coord + y
        
        x_coord_td = x_coord + rot_la[0,0]
        y_coord_td = y_coord + rot_la[0,1]
        

    else:
        x_coord_td = 0
        y_coord_td = 0
    
    
    datetime_obj = datetime.fromtimestamp(first_sample_time, tz=timezone.utc)
    trace.time = ampl_time_rel2trg_corr
    trace.dt = ampl_scan_interval
    trace.data = np.float32(envelope_data_at_desired)
    
    trace.header['TRACE_SEQUENCE_LINE'] = trace_num
    trace.header['TRACE_SEQUENCE_FILE'] = trace_num
    trace.header['FieldRecord'] = 1
    trace.header['TraceNumber'] = 1
    trace.header['EnergySourcePoint'] = trace_num
    trace.header['TraceIdentificationCode'] = 1
    trace.header['NSummedTraces'] = 1
    trace.header['NStackedTraces'] = 1
    trace.header['DataUse'] = 1
    trace.header['ReceiverGroupElevation'] = z_offset
    trace.header['SourceDepth'] = z_offset
    trace.header['SourceWaterDepth'] = sounding_depth
    trace.header['GroupWaterDepth'] = sounding_depth
    trace.header['ElevationScalar'] = -100
    trace.header['SourceGroupScalar'] = -100
    
    trace.header['SourceX'] = int(np.rint(x_coord_td*100))
    trace.header['SourceY'] = int(np.rint(y_coord_td*100))
    trace.header['GroupX'] = int(np.rint(x_coord_td*100))
    trace.header['GroupY'] = int(np.rint(y_coord_td*100))
    trace.header['CoordinateUnits'] = 1
    
    trace.header['DelayRecordingTime'] = int(np.rint(delay))
    trace.header['TRACE_SAMPLE_COUNT'] = len(desired_sample_times)
    trace.header['TRACE_SAMPLE_INTERVAL'] = int(np.rint(ampl_scan_interval*(10**6)))  # in microsecs
    
    trace.header['Correlated'] = 1
    trace.header['SweepFrequencyStart'] = sounding.slf_freq
    trace.header['SweepFrequencyEnd'] = sounding.slf_freq + sounding.freq_shift
    trace.header['SweepLength'] = int(np.rint(sounding.pulse_len*1000))
    trace.header['SweepType'] = 4
    
    trace.header['YearDataRecorded'] = datetime_obj.year
    trace.header['DayOfYear'] = datetime_obj.day
    trace.header['HourOfDay'] = datetime_obj.hour
    trace.header['MinuteOfHour'] = datetime_obj.minute
    trace.header['SecondOfMinute'] = datetime_obj.second
    trace.header['TimeBaseCode'] = 4  # 4 - UTC
    
    trace.header['TraceValueMeasurementUnit'] = 3
    
    
    return trace


def get_traces(idx_path, coord_transf, delay=0, tracelen=250):  # delay and tracelen in ms

    acf_path = idx_path[:-4]
    
    asd_obj_list = ASDfile.create_from_idx_file(idx_path)
    
    traces = []
    
    # Load acf file into the memory
    with open(acf_path, 'rb') as f1:
        buffer = f1.read()
    
    trace_num = 1
    
    obj: ASDfile
    for obj in asd_obj_list[:]:
        asd.parse_xml_header(obj, buffer)
        asd.parse_bin_header(obj, buffer)

        for sounding in obj.soundings[:]:
            trace = proc_trace(trace_num, coord_transf, sounding, obj, tracelen=tracelen, delay=delay)
            trace.acf = os.path.basename(acf_path)
            traces.append(trace)
            trace_num += 1
            
    return traces
