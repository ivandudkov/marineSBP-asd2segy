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
        
def proc_trace(sounding: Sounding, delay=0, tracelen=200):
    # complex_trace = sounding.data_array[:,0] + sounding.data_array[:,1]  # complex array
    # complex_trace = sounding.data_array[:,0]

    
    sample_st = sounding.ampl_time_rel2trg
    sample_dt = sounding.ampl_scan_interval
    
    resampl_real = resample_trace(sounding.data_array[:,0], sample_dt, sample_dt/4)
    resampl_imag = resample_trace(sounding.data_array[:,1], sample_dt, sample_dt/4)
    
    complex_trace = resampl_real + resampl_imag
    # As it turned out, the sample start time given
    # relative to zero, i.e. sample_st/sample_dt is integer (like 198.999999 i.e. 199)
    index_start = int(np.ceil(sample_st/sample_dt))
    
    ampl_new = []
    sample_times = [sample_st + x*sample_dt for x in np.arange(complex_trace.shape[0]+index_start)]
    
    for i in np.arange(complex_trace.shape[0]+index_start):
        if i < index_start:
            ampl_new.append(0.0)
        else:
            ampl_new.append(complex_trace[i-index_start])

    return ampl_new, sample_times
    
    # plot_signal(complex_trace, 
    #             sample_times[index_start:], 
    #             ampl_new, 
    #             sample_times)
    



