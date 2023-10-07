import os
import numpy as np
import matplotlib.pyplot as plt
import time

import asd
import xmlheader_parse
import idxfile_parse
import ping_datablock_parse
import proc_trace

def plot_seismic_traces():
    pass


idx_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf.idx'
acf_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf'


idx_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2022-06-17T054120Z_04061504.asd.acf.idx'
acf_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2022-06-17T054120Z_04061504.asd.acf'

asd_obj_list = asd.ASDfile.create_from_idx_file(idx_file)
asd_obj = asd_obj_list[0]

with open(acf_file, 'rb') as f1:
    buffer = f1.read()

print('________________________________')

# xmlheader_parse.parse_xml_header(asd_obj, buffer)
# ping_datablock_parse.parse_bin_header(asd_obj, buffer)


traces = []
start_times = []

delay = 0.010  # s; 10 ms
trace_len = 0.15  # s; 150 ms

num_of_traces = 0
for obj in asd_obj_list[0:1000]:
    xmlheader_parse.parse_xml_header(obj, buffer)
    ping_datablock_parse.parse_bin_header(obj, buffer)

    for sounding in obj.soundings[:]:
        # print(sounding.ampl_time_rel2trg)
        # print(sounding.ampl_scan_interval*1000)
        ampls, times = proc_trace.proc_trace(sounding, obj)
        
        data_array = np.ones((len(ampls), 2))
        data_array[:, 0] = ampls
        data_array[:, 1] = times
        
        traces.append(data_array)
        num_of_traces += 1
        
    if num_of_traces >= 3000:
        break
    
# print(len(traces))
# print(traces[0].shape)

trace_array = np.zeros((len(traces), 2, 2500))
print(trace_array.shape)
for i, trace in enumerate(traces):
    trace_array[i,0,0:np.shape(trace)[0]] = trace[:,0]
    trace_array[i,1,0:np.shape(trace)[0]] = trace[:,1]


def plot_rawtraces(raw_traces):
    # clip = 1e+4
    # vmin, vmax = -clip, clip

    # Figure
    figsize=(15, 20)
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor='w', edgecolor='k',
                        squeeze=False,
                        sharex=True)
    axs = axs.ravel()
    im = axs[0].imshow(raw_traces[:,0,:].T, cmap=plt.cm.seismic)
    # im = axs[0].imshow(raw_traces[:,0,:].T, cmap=plt.cm.seismic, vmin=vmin, vmax=vmax)
    plt.show()
    
plot_rawtraces(trace_array[:,:,100:700])