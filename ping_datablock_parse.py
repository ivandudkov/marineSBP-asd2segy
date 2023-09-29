import os
import struct

from datetime import datetime, time, date
from dataclasses import dataclass, field
from collections import defaultdict, namedtuple

import numpy as np

from asd import ASDfile
from classes_from_xml import Sounding

header_decoder = {'bin_sep': struct.Struct('>4s'),
                  'head_len': struct.Struct('>H'),
                  'b_per_sample': struct.Struct('>H'),
                  'num_sample': struct.Struct('>I'),
                  'version': struct.Struct('>4s'),
                  'd_type': struct.Struct('>4s'),
                  'ident_num': struct.Struct('>8s'),
                  'subsid_num': struct.Struct('>H'),
                  'flag': struct.Struct('>H')}


def parse_bin_header(asd_obj: ASDfile, buffer):
    asd_bin_part = buffer[asd_obj.start_byte + asd_obj.xml_size:asd_obj.end_byte+1]
    no_of_soundings = asd_obj.no_of_soundings
    bin_sep = b'\xff\xff\xff\xff'
    
    if len(asd_obj.soundings) == no_of_soundings:
        pass
    else:
        raise RuntimeError('Number of soundings does not equal num of sounding objects!')
    
    def read_bin_header(buffer_pos, buffer, sounding_obj: Sounding):
        # 0 ... 3: Binary Header Separator
        bin_sep = struct.Struct('>4s')
        bin_separator = bin_sep.unpack(buffer[buffer_pos:buffer_pos+bin_sep.size])
        buffer_pos = buffer_pos + bin_sep.size
        # 4 ... 5 Header Length (32 Byte)
        head_len = struct.Struct('>H')
        head_length = head_len.unpack(buffer[buffer_pos:buffer_pos+head_len.size])
        buffer_pos = buffer_pos + head_len.size
        # 6 ... 7 Byter Per Sample
        b_per_sample = struct.Struct('>H')
        bytes_per_sample = b_per_sample.unpack(buffer[buffer_pos:buffer_pos+b_per_sample.size])
        buffer_pos = buffer_pos + b_per_sample.size
        # 8 ... 11 Number of Samples (h=0..F)
        num_sample = struct.Struct('>I')
        number_samples = num_sample.unpack(buffer[buffer_pos:buffer_pos+num_sample.size])
        # number_of_samples = int.from_bytes(number_samples[0], byteorder='big')
        buffer_pos = buffer_pos + num_sample.size
        # 12 ... 15 Header Version (0100 for Version 1.0)
        h_ver = struct.Struct('>4s')
        header_version = h_ver.unpack(buffer[buffer_pos:buffer_pos+h_ver.size])
        header_version = header_version[0].decode(encoding='utf-8', errors='strict')
        buffer_pos = buffer_pos + h_ver.size
        # 16 ... 19 Data Type, e.g. _PAR/_PLF etc (_ is a space; 0x20)
        d_type = struct.Struct('>4s')
        data_type = d_type.unpack(buffer[buffer_pos:buffer_pos+d_type.size])
        data_type = data_type[0].decode(encoding='utf-8', errors='strict')
        buffer_pos = buffer_pos + d_type.size
        # 20 ... 27 Ident Number (resp. # see below)
        ident_num = struct.Struct('>8s')
        ident_number = ident_num.unpack(buffer[buffer_pos:buffer_pos+ident_num.size])
        ident_number = ident_number[0].decode(encoding='utf-8', errors='strict')
        buffer_pos = buffer_pos + ident_num.size
        # 28 ... 29 Subsident Number (vers. 1.1)
        subsid_num = struct.Struct('>H')
        subsident_num = subsid_num.unpack(buffer[buffer_pos:buffer_pos+subsid_num.size])
        buffer_pos = buffer_pos + subsid_num.size
        # 30 ... 31 Flags 0..15; 0 - Complex Sample, 1 - Polar Coordinates, 2..15 - Reserve
        # 0000 - real nums, 0001 - complex numbers with real and imaginary part
        fl = struct.Struct('>H')
        flags = fl.unpack(buffer[buffer_pos:buffer_pos+fl.size])
        buffer_pos = buffer_pos + fl.size
        
        sounding_obj.bh_sep = bin_separator[0]
        sounding_obj.bh_len = head_length[0]
        sounding_obj.bh_bytes_per_sample = bytes_per_sample[0]
        sounding_obj.bh_sample_no = number_samples[0]
        sounding_obj.bh_head_ver = header_version
        sounding_obj.bh_data_type = data_type
        sounding_obj.bh_ident_num = ident_number
        sounding_obj.bh_subident_num = subsident_num[0]
        sounding_obj.bh_flag = flags[0]
        
        return buffer_pos
    
    def read_bin_data(buffer_pos, buffer, sounding_obj: Sounding):
        samp = struct.Struct('>ll')
        no_scans = sounding_obj.bh_sample_no
        data_array = np.ones((no_scans, 3))

        
        for i in range(no_scans):
            sample = samp.unpack(buffer[buffer_pos:buffer_pos+samp.size])
            
            data_array[i, 0] = sample[0]
            data_array[i, 1] = sample[1]
            data_array[i, 2] = i*sounding_obj.ampl_scan_interval
            
            buffer_pos = buffer_pos + samp.size
        
        sounding_obj.data_array = data_array
        
        return buffer_pos
    
    buffer_pos = 0
    for sounding in asd_obj.soundings:
        buffer_pos = read_bin_header(buffer_pos, asd_bin_part, sounding)
        buffer_pos = read_bin_data(buffer_pos, asd_bin_part, sounding)
        

    
    
    