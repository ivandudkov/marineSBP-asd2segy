import os

import asd
import xmlheader_parse
import idxfile_parse

idx_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf.idx'
acf_file = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\SEB\PS3SLF_2021-09-17T110351Z_00047728.asd.acf'

asd_obj_list = asd.ASDfile.create_from_idx_file(idx_file)

for asd_obj in asd_obj_list[0:2]:
    print(asd_obj.acf_name)


with open(acf_file, 'rb') as f1:
    buffer = f1.read()

for asd_obj in asd_obj_list[0:1]:
    xml_root = xmlheader_parse.parse_xml_header(asd_obj, buffer)
    
# for child in xml_root[1][2]:
#     print(child.tag, child.attrib)
    
print(xml_root[1][1][0].text)