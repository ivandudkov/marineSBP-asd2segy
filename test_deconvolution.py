
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

# datapath = r'G:\ABP_48\Parasound\ABP48\ASD\SLF'
# idx_files_list = fes.file_ext_search('.idx', datapath)


from asd import  ASDfile
from xml_classes import Sounding

crs_wgs84 = CRS.from_epsg(4326)
crs_utm35n = CRS.from_epsg(32635)
crs_utm34n = CRS.from_epsg(32634)

coord_transf = Transformer.from_crs(crs_wgs84, crs_utm34n, always_xy=True)

delay = 0
tracelen = 250

for no, idx_path in enumerate(idx_files_2[1:2]):
    acf_path = idx_path[:-4]
    asd_obj_list = ASDfile.create_from_idx_file(idx_path)
    
    traces = []
    
    # Load acf file into the memory
    with open(acf_path, 'rb') as f1:
        buffer = f1.read()
    
    trace_num = 1
    
    obj: ASDfile
    for obj in asd_obj_list[0:1]:
        asd.parse_xml_header(obj, buffer)
        asd.parse_bin_header(obj, buffer)

        sounding: Sounding
        for sounding in obj.soundings[0:1]:
            try:
                trace = trace_proc.proc_trace(trace_num, coord_transf, sounding, obj, tracelen=tracelen, delay=delay)
                trace.acf = os.path.basename(acf_path)
                traces.append(trace)
                trace_num += 1
            
            except:
                pass