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
    index_start = int(np.ceil(sample_st/sample_dt))
    
    sample_times = [sample_st + x*sample_dt for x in np.arange(sample_array.shape[0])]
    sample_times_shifted = [x*sample_dt for x in np.arange(sample_array.shape[0] + index_start)]
    
    func = interpolate.interp1d(sample_times, sample_array, fill_value=0)
    shifted_samples = func(sample_times_shifted)
    
    return shifted_samples, sample_times_shifted
        
def proc_trace(sounding: Sounding, delay=0, tracelen=200):
    complex_trace = sounding.data_array[:,0] + sounding.data_array[:,1]  # complex array
    
    sample_interval = sounding.ampl_scan_interval
    start_time = sounding.ampl_time_rel2trg
    
    sample_times = [start_time + x*sample_interval for x in np.arange(complex_trace.shape[0])]
    
    data_array = np.ones((np.shape(complex_trace)[0], 2))
    data_array[:, 0] = complex_trace
    data_array[:, 1] = sample_times
    
    index_start = int(np.ceil(start_time/sample_interval))
    new_sample_times = [x*sample_interval for x in np.arange(complex_trace.shape[0] + int(start_time/sample_interval))]
    
    f = interpolate.interp1d(data_array[:,1], data_array[:,0], fill_value=0)
    
    print(index_start)
    print(start_time/sample_interval)
    print(1/12207)
    new_ampls = f(new_sample_times[index_start:])
    
    # plot_signal(data_array[:,0], data_array[:,1], new_ampls, new_sample_times[index_start:])
    



