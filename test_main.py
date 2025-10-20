import os
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj, CRS, Transformer
import segyio

import file_ext_search as fes

import asd
import trace_proc


class MySpec(object):
    def __init__(self):
        self.iline = 189  # default value for segyio
        self.xline = 193  # default value for segyio
        self.tracecount = 0
        self.samples = []  # sample times, a list
        self.ext_headers = 0
        self.format = 1  # 1 - IBM Float; 5 - 4-byte IEEE float
        self.endian = 'big'

idx_file2 = r'C:\YandexDisk\MyProjects\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf.idx'
acf_file2 = r'C:\YandexDisk\MyProjects\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf'


idx_file = r'C:\YandexDisk\MyProjects\InspectingP70Data\P70_data\SEB\Prof2_abp56_Gd\PS3SLF_2024-07-07T174231Z_07793648.asd.acf.idx'
acf_file = r'C:\YandexDisk\MyProjects\InspectingP70Data\P70_data\SEB\Prof2_abp56_Gd\PS3SLF_2024-07-07T174231Z_07793648.asd.acf'

idx_files_2 = [idx_file2, idx_file]

# datapath = r'D:\ABP49_Processing\abp49_GdGot'
# idx_files_list = fes.file_ext_search('.idx', datapath)

# OLD STABLE VERSION

path = r'C:\Data\P70_Converter_Testing'
from trace_proc import int_header


import threading
import os

# Coords
espg_code = 32634  # UTM34N
crs_wgs84 = CRS.from_epsg(4326)
crs_xy = CRS.from_epsg(espg_code)
coord_transf = Transformer.from_crs(crs_wgs84, crs_xy, always_xy=True)

delay = 0
tracelen = 250



def task(idx_files):
    
    file_count = len(idx_files)
    
    for no, idx_file in enumerate(idx_files):
        print(f'Converting file {no} of {file_count}')
    
        traces = trace_proc.get_traces(idx_file, coord_transf, delay=delay, tracelen=tracelen)

        myspec = MySpec()
        myspec.tracecount = len(traces)
        myspec.samples = np.arange(delay,delay+tracelen+traces[0].dt*1000,traces[0].dt*1000)
        
        fname = traces[0].acf[:-8] + '.sgy'
        save_to = os.path.join(path, fname)

        with segyio.create(save_to, myspec) as f5:
            for num, trace in enumerate(traces):
                f5.trace[num] = trace.data
                
                for key in int_header.keys():
                    f5.header[num][int_header[str(key)]] = trace.header[str(key)]


task(idx_files=idx_files_2[1:2])

# POS EXPORT FROM ACF
save_to = r'C:\Data\test\ABP49_SLF.csv'

for idx_file in idx_files:
    pos_strings = trace_proc.get_pos_acf(idx_file)
    
    
    if os.path.exists(save_to):
        with open(save_to, 'a+') as f9:
            for line in pos_strings:
                f9.write(f'{line}\n')
    else:
        with open(save_to, 'w') as f9:
            f9.write('num,acf,asd,ISOdatetime,POSIXsec,lat,lon\n')
            
            for line in pos_strings:
                f9.write(f'{line}\n')