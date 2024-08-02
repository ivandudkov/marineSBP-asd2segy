import numpy as np
from scipy import signal, interpolate
import matplotlib.pyplot as plt

from asd import ASDfile
from xml_classes import Sounding

from numpy import cos, sin


class Trace:
    
    def __init__(self) -> None:
        
        # Bytes 1 - 20
        self.trace_index = 0
        self.trace_seq_num_line = 0
        self.trace_seq_num_reel = 0
        self.ffid = 0
        self.trace_num_field_record = 0
        self.sp = 0
        
        # Bytes 21 - >>
        self.trace_num = 0
        self.trace_id = 0
        self.num_of_vert_sum_traces = 0
        self.num_of_horiz_sum_traces = 0
        self.data_use = 0  # 1 - production, 2 - test
        
        # Bytes 37 - 70
        self.dist_from_source_to_receiv = 0
        self.receiv_group_elev = 0
        self.surface_elev_at_source = 0
        self.source_depth_below_sufr = 0
        self.datum_elev_at_receiv_grp = 0
        self.datum_elev_at_source = 0
        self.water_depth_at_source = 0
        self.water_depth_at_group = 0
        self.scaler_to_all_elev_and_depth = 0
        
        # Coordinates, bytes 71 - 90
        self.scaler_to_all_coordinates = 0
        self.source_x_coord = 0
        self.source_y_coord = 0
        self.group_x_coord = 0  # receiver
        self.group_y_coord = 0  # receiver
        self.coordinate_units = 0  # 1 - lenm/ft, 2 - secarc
        
        # bytes 91 - 108 - NOTHING
        
        # bytes 109-110
        self.delay_rec_time = 0  # in ms
        
        # bytes 115-118
        self.num_of_samples = 0
        self.sample_interval = 0
        
        # bytes 119 - 124
        self.gain_type_of_instruments = 0
        self.instrument_gain = 0
        self.instrument_gain_constant = 0
        
        
        # bytes 125 - 140
        self.correlated = 0  # 1 - yes, 2 - no
        self.sweep_freq_start = 0  # sweep frequency at start
        self.sweep_freq_end = 0  # sweep frequency at end
        self.sweep_length_in_ms = 0
        self.sweep_type = 0  # 1 - lin, 2 - parabol, 3 - exp, 4 - other
        self.sweep_trace_taper_len_at_start = 0  # in ms
        self.sweep_trace_taper_len_at_end = 0  # in ms
        self.taper_type = 0  # 1 - lin, 2 - cos, 3 - other
        
        # bytes 141-156 - NOTHING
        
        # bytes 157 - 170
        self.year = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.time_basis = 0  # 1 - local, 2 - GMT, 3 - other
        
        # OUT OF THE HEADER
        self.millisecond = 0
        
        self.trace_data = []
        
        
    
    
    

def plot_signal2(x_old, y_old, x_new, y_new):
    # plt.plot(x_old, y_old, 'o', x_new, y_new, '-')
    plt.plot(x_old, y_old, '_')
    plt.plot(x_new, y_new, '|')
    plt.show()
    
def plot_signal(x_old, y_old, x_new, y_new):
    # plt.plot(x_old, y_old, 'o', x_new, y_new, '-')
    plt.plot(x_old, y_old)
    plt.plot(x_new, y_new)
    plt.show()

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

def filter_heave(heave, heave_quality):
    for i, qual in enumerate(heave_quality):
        if qual == 'p':
            pass
        else:
            pass
            heave.pop(i)

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


def heave_correction(asd_obj: ASDfile):
    draught = asd_obj.general.draught
    print(draught)
    print(asd_obj.general.is_draught_corrected)


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


# Нужно указать sample start time и trace len
# функция proc_trace должна выдать массивы и заголовки, готовые для записи seg-y в segyio
def proc_trace(sounding: Sounding, asd_obj: ASDfile, delay=0, tracelen=0.2):  # delay and tracelen in s
    
    ampl_time_rel2trg = sounding.ampl_time_rel2trg  # in secs
    ampl_scan_interval = sounding.ampl_scan_interval  # in secs
    trg_time = sounding.trg_time  # posix seconds, absolute time

    # reference_intensity = 6.67*10**-19  # W/m^2, in Sea Water muPa at 1m
    # source_intensity = 10**((sounding.src_level + 10*np.log10(reference_intensity))/10)
    # print(f'Source Intensity (approximate): {source_intensity}')
    
    adc_scale_factor = asd_obj.general.adc_scale_factor
     
    # Heave part
    sv_keel = asd_obj.general.sv_keel  # m/s
    heave = asd_obj.motion.heave  # [[m],[posix seconds]]
    heave_quality = asd_obj.motion.quality[:-1] 
    heave_func = interpolate.interp1d(heave[:,1], heave[:,0], fill_value=0)
    heave_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)
    heave_correction_secs = heave_at_ampl_time/sv_keel*2
    
    # Roll
    roll = asd_obj.motion.roll
    roll_func = interpolate.interp1d(roll[:,1], roll[:,0], fill_value=0)
    roll_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)
    
    # Pitch
    pitch = asd_obj.motion.pitch
    pitch_func = interpolate.interp1d(pitch[:,1], pitch[:,0], fill_value=0)
    pitch_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)
    
    # Yaw
    yaw = asd_obj.heading.heading
    yaw_func = interpolate.interp1d(yaw[:,1], yaw[:,0], fill_value=0)
    yaw_at_ampl_time = heave_func(trg_time + ampl_time_rel2trg)
    
    rotation_matrix = euler_angle_rot_matrix(roll_at_ampl_time, pitch_at_ampl_time, yaw_at_ampl_time)
    
    # print(asd_obj.installation.__dict__)
    p70_lever_arm = np.array([asd_obj.installation.tx_x, asd_obj.installation.tx_y, asd_obj.installation.tx_z]).reshape((3, 1))
    
    
    rotated_la = rotation_matrix @ p70_lever_arm
    # print(rotated_la)
    tx_z_rot = rotated_la[0,2][0]
    rot_diff = asd_obj.installation.tx_z - tx_z_rot
    # print(tx_z_rot[0])
    # print(rot_diff)
    # print(heave_at_ampl_time)

    heave_correction_secs = (heave_at_ampl_time*2)/sv_keel
    wl_corr = tx_z_rot/sv_keel*2

    ampl_time_rel2trg_corr = ampl_time_rel2trg - heave_correction_secs
    
    complex = complex_trace(sounding.data_array[:,0], sounding.data_array[:,1])
    envelope_data = np.abs(complex)
    
    # Real part of the complex trace is an acoustic amplitude
    # sounding.data_array[:,0] - real part of the complex trace, amplitude vallues
    # sounding.data_array[:,1] - imag part of the complex trace
    # complex = complex_trace(sounding.data_array[:,0], sounding.data_array[:,1])
    
    # Original Sample Times
    sample_times = [ampl_time_rel2trg_corr + x*ampl_scan_interval for x in np.arange(envelope_data.shape[0])]
    
    # print(sample_times)
    # Desired Sample Times
    desired_sample_times = np.arange(delay,delay+tracelen+ampl_scan_interval,ampl_scan_interval)
    
    # Resample data again using desired Sample Times
    func = interpolate.CubicSpline(sample_times, envelope_data, extrapolate=False)
    
    # Data at desired Sample Times and replace numpy 'nan' values by 0
    envelope_data_at_desired = np.nan_to_num(func(desired_sample_times))
    
    return envelope_data_at_desired, desired_sample_times, ampl_scan_interval


