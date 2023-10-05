import numpy as np
from scipy import signal

from asd import ASDfile
from classes_from_xml import Sounding


class Trace:
    
    def __init__(self) -> None:
        pass

def resample_trace(ampls, dt, new_dt):
    num = round(dt*np.shape(ampls)[0]/new_dt)
    ampls_resampled = signal.resample(x=ampls, num=num)
    return ampls_resampled

def proc_trace(sounding: Sounding, delay=0, tracelen=200):
    complex_trace = sounding.data_array[:,0] + sounding.data_array[:,1]  # complex array
    
    sample_times = [x*sounding.ampl_scan_interval for x in np.arange(complex_trace.shape[0])]
    
    data_array = np.ones((np.shape(complex_trace)[0], 2))
    data_array[:, 0] = complex_trace
    data_array[:, 1] = sample_times
    
    print(sample_times)
    
    print(sounding.ampl_time_rel2trg/sounding.ampl_scan_interval)
    
    # import matplotlib.pyplot as plt
    # plt.plot(data_array[:, 0], data_array[:, 1], 'go-')
    # plt.plot(data_res, time_res, '.-')
    # plt.legend(['data', 'resampled'], loc='best')
    # plt.show()
    



