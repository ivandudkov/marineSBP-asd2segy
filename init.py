import os
import numpy as np
import matplotlib.pyplot as plt
import time

import asd
import xmlheader_parse
import idxfile_parse
import ping_datablock_parse

def plot_seismic_traces():
    pass


idx_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf.idx'
acf_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf'

asd_obj_list = asd.ASDfile.create_from_idx_file(idx_file)
asd_obj = asd_obj_list[0]

with open(acf_file, 'rb') as f1:
    buffer = f1.read()

print(len(buffer))

print('________________________________')


xmlheader_parse.parse_xml_header(asd_obj, buffer)
ping_datablock_parse.parse_bin_header(asd_obj, buffer)

print(asd_obj.soundings[0].data_array)
# plt.plot(asd_obj.motion.roll[:,1], asd_obj.motion.roll[:,0], color='green')
# plt.plot(asd_obj.motion.pitch[:,1], asd_obj.motion.pitch[:,0], color='red')
# plt.plot(asd_obj.motion.heave[:,1], asd_obj.motion.heave[:,0], color='blue')
# plt.plot(asd_obj.heading.heading[:,1], asd_obj.heading.heading[:,0], color='brown')
# plt.show()
# start_time = time.time()
# for asd_obj in asd_obj_list:
#     xmlheader_parse.parse_xml_header(asd_obj, buffer)
    # plt.plot(asd_obj.position.latlon[:,1], asd_obj.position.latlon[:,0], color='green')
# end_time = time.time()
# print(f'Elapsed time: {end_time - start_time:.2f} secs')
# # print(asd_obj.position.latlon)
# plt.show()