import numpy as np
from scipy import signal, interpolate
import matplotlib.pyplot as plt

from asd import ASDfile
from xml_classes import Sounding


class Trace:
    
    def __init__(self) -> None:
        pass

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


# Нужно указать sample start time и trace len
# функция proc_trace должна выдать массивы и заголовки, готовые для записи seg-y в segyio
def proc_trace(sounding: Sounding, asd_obj: ASDfile, delay=0, sample_dt=0, tracelen=200):  # delay and tracelen in ms
    
    ampl_time_rel2trg = sounding.ampl_time_rel2trg  # in secs
    ampl_scan_interval = sounding.ampl_scan_interval  # in secs
    trg_time = sounding.trg_time  # posix seconds, absolute time
    sv_keel = asd_obj.general.sv_keel  # m/s
    heave = asd_obj.motion.heave  # [[m],[posix seconds]]
    heave_quality = asd_obj.motion.quality[:-1]
    delay = delay/1000
    tracelen = tracelen/1000
    
    if sample_dt == 0:
        sample_dt = ampl_scan_interval
    else:
        sample_dt = sample_dt/1000
       
         
    heave_func = interpolate.interp1d(heave[:,1], heave[:,0], fill_value=0)
    # print(heave_func(abs_time+sample_st))
        
    
    # Real part of the complex trace is an acoustic amplitude
    # sounding.data_array[:,0] - real part of the complex trace, amplitude vallues
    # sounding.data_array[:,1] - imag part of the complex trace
    # Original Sample Times
    sample_times = [ampl_time_rel2trg + x*ampl_scan_interval for x in np.arange(sounding.data_array[:,0].shape[0])]
    
    # Desired Sample Times
    desired_sample_times = np.arange(delay,tracelen+sample_dt,sample_dt)
    
    # Resample data again using desired Sample Times
    func = interpolate.CubicSpline(sample_times, sounding.data_array[:,0], extrapolate=False)
    
    # Data at desired Sample Times and replace numpy 'nan' values by 0
    data_at_desired = np.nan_to_num(func(desired_sample_times))
    
    return data_at_desired, desired_sample_times


