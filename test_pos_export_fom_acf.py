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

idx_file2 = r'D:\aa_yandexcloud\MyProjects\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf.idx'
acf_file2 = r'D:\aa_yandexcloud\MyProjects\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf'


idx_file = r'D:\aa_yandexcloud\MyProjects\InspectingP70Data\P70_data\SEB\Prof2_abp56_Gd\PS3SLF_2024-07-07T174231Z_07793648.asd.acf.idx'
acf_file = r'D:\aa_yandexcloud\MyProjects\InspectingP70Data\P70_data\SEB\Prof2_abp56_Gd\PS3SLF_2024-07-07T174231Z_07793648.asd.acf'

idx_files_2 = [idx_file2, idx_file]

datapath = r'G:\ABP_48\Parasound\ABP48\ASD\SLF'
idx_files_list = fes.file_ext_search('.idx', datapath)



save_to = r'C:\Data\test\ABP48_SLF.csv'

for idx_file in idx_files_list:
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