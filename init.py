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

asd_obj_list = asd.ASDfile.create_from_idx_file(idx_file)
asd_obj = asd_obj_list[0]

with open(acf_file, 'rb') as f1:
    buffer = f1.read()

print('________________________________')

# xmlheader_parse.parse_xml_header(asd_obj, buffer)
# ping_datablock_parse.parse_bin_header(asd_obj, buffer)


traces = []
start_times = []

num_of_traces = 0
for obj in asd_obj_list[0:1]:
    xmlheader_parse.parse_xml_header(obj, buffer)
    ping_datablock_parse.parse_bin_header(obj, buffer)

    for sounding in obj.soundings[0:1]:
        print(sounding.ampl_time_rel2trg)
        print(sounding.ampl_scan_interval*1000)
        proc_trace.proc_trace(sounding)
        
        
    #     start_times.append(sounding.ampl_starttimerel2trg)
    #     traces.append(sounding.data_array)
    #     num_of_traces += 1
        
    # if num_of_traces >= 3000:
    #     break

# print(len(traces))
# print(traces[0])
# trace_array = np.zeros((len(traces), 1000))

# for i, trace in enumerate(traces):
#     trace_array[i,0:np.shape(trace)[0]] = trace[:]


def plot_rawtraces(raw_traces):
    clip = 1e+4
    vmin, vmax = -clip, clip

    # Figure
    figsize=(15, 15)
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor='w', edgecolor='k',
                        squeeze=False,
                        sharex=True)
    axs = axs.ravel()
    im = axs[0].imshow(raw_traces.T, cmap=plt.cm.seismic, vmin=vmin, vmax=vmax)
    plt.show()
    
# plot_rawtraces(trace_array[:])