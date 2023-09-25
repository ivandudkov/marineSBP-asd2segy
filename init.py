import os

import asd
import xmlheader_parse
import idxfile_parse

idx_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf.idx'
acf_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf'

asd_files = idxfile_parse.read_idx_file(idx_file)



asd_obj_list = asd.ASDfile.create_from_idx_file(idx_file)

for asd_obj in asd_obj_list[0:2]:
    print(asd_obj.acf_name)


with open(acf_file, 'rb') as f1:
    buffer = f1.read()

asd.ASDfile.get_xml_sizes(asd_obj_list[0:2], buffer)

for asd_obj in asd_obj_list[0:2]:
    print(asd_obj.xml_size)