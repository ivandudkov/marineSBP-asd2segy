import numpy as np
from scipy import signal, interpolate
import matplotlib.pyplot as plt

from asd import ASDfile
from classes_from_xml import Sounding


class Trace:
    
    def __init__(self) -> None:
        pass

def plot_signal(x_old, y_old, x_new, y_new):
    # plt.plot(x_old, y_old, 'o', x_new, y_new, '-')
    plt.plot(x_old, y_old, '_')
    plt.plot(x_new, y_new, '|')
    plt.show()

def resample_trace(ampls, dt, new_dt):
    num = round(dt*np.shape(ampls)[0]/new_dt)
    ampls_resampled = signal.resample(x=ampls, num=num)
    return ampls_resampled

def shift_data_to_zero_start(sample_st, sample_dt, sample_array):
    # As it turned out, the sample start time given
    # relative to zero, i.e. sample_st/sample_dt is integer (like 198.999999 i.e. 199)
    index_start = int(np.ceil(sample_st/sample_dt))
    
    sample_times = [sample_st + x*sample_dt for x in np.arange(sample_array.shape[0])]
    sample_times_shifted = [x*sample_dt for x in np.arange(sample_array.shape[0] + int(sample_st/sample_dt))]
    
    func = interpolate.interp1d(sample_times, sample_array, fill_value=0)
    shifted_samples = func(sample_times_shifted[index_start:])
    
    print(sample_st/sample_dt)
    
    # plot_signal(sample_array, 
    #             sample_times, 
    #             shifted_samples, 
    #             sample_times_shifted[index_start:])
    
    
    return shifted_samples, sample_times_shifted, index_start
        
def shift_trace_by_heave():
    pass
        
def proc_trace(sounding: Sounding, asd_obj: ASDfile, delay=0, tracelen=200):
    # complex_trace = sounding.data_array[:,0] + sounding.data_array[:,1]  # complex array
    # complex_trace = sounding.data_array[:,0]

    
    sample_st = sounding.ampl_time_rel2trg
    sample_dt = sounding.ampl_scan_interval
    abs_time = sounding.trg_time
    surf_ss = asd_obj.general.sv_keel
    heave = asd_obj.motion.heave
    heave_quality = asd_obj.motion.quality[:-1]
    
    for i, qual in enumerate(heave_quality):
        if qual == 'p':
            pass
        else:
            pass
            # heave.pop(i)
    heave_func = interpolate.interp1d(heave[:,1], heave[:,0], fill_value=0)
    
    # print(heave_func(abs_time+sample_st))
    
    resampl_real = resample_trace(sounding.data_array[:,0], sample_dt, sample_dt)
    resampl_imag = resample_trace(sounding.data_array[:,1], sample_dt, sample_dt)
    
    complex_trace = np.ones(resampl_real.shape, dtype=complex)
    complex_trace.real = resampl_real
    complex_trace.imag = resampl_imag

    # As it turned out, the sample start time given
    # relative to zero, i.e. sample_st/sample_dt is integer (like 198.999999 i.e. 199)
    index_start = int(np.ceil(sample_st/sample_dt))
    
    ampl_new = []
    sample_times = [sample_st + x*sample_dt for x in np.arange(complex_trace.shape[0]+index_start)]
    
    
    abs_value = np.sqrt(complex_trace.real**2 + complex_trace.imag**2)
    
    for i in np.arange(abs_value.shape[0]+index_start):
        if i < index_start:
            ampl_new.append(0.0)
        else:
            ampl_new.append(abs_value[i-index_start])
    
    # plot_signal(abs_value, 
    #             sample_times[index_start:], 
    #             ampl_new, 
    #             sample_times)
    
    
    
    
    return ampl_new, sample_times



