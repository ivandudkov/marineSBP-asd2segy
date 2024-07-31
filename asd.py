import os
import struct
import xml.etree.ElementTree as ET

import numpy as np



import idxfile

from xml_classes import Installation, MotionData, HeadingData,\
                             PositionData, SpeedCourseData, DepthData,\
                             PS3Config, GeneralSettings, Sounding, PulseTarget


header_decoder = {'bin_sep': struct.Struct('>4s'),
                  'head_len': struct.Struct('>H'),
                  'b_per_sample': struct.Struct('>H'),
                  'num_sample': struct.Struct('>I'),
                  'version': struct.Struct('>4s'),
                  'd_type': struct.Struct('>4s'),
                  'ident_num': struct.Struct('>8s'),
                  'subsid_num': struct.Struct('>H'),
                  'flag': struct.Struct('>H')}


class ASDfile():
    """A class representing ASD file"""
    
    def __init__(self) -> None:
        self.name = ''
        self.is_grouped_acf = False
        self.acf_fpath = ''
        self.idx_fpath = ''
        self.start_byte = 0
        self.end_byte = 0
        self.size = 0
        self.xml_size = 0
        self.bin_size = 0
        self.datablock_size = 0
        
        # Basic Info
        self.xml_schema = ''
        self.system = ''
        self.cm_version = ''
        self.spm_version = ''
        self.tbf_version = ''
        self.spmfpga_version = ''
        self.dm80_version = ''
        self.doc_daytime = ''
        self.no_of_soundings = int()
        self.reduced_asd = ''
        
        # AUX
        self.aux_base_time = float()
        self.installation = Installation()
        self.motion = MotionData()
        self.heading = HeadingData()
        self.position = PositionData()
        self.speed_course = SpeedCourseData()
        self.depths = []  # multiple Depth classes
        
        self.ps3config = PS3Config()
        self.general = GeneralSettings()
        
        self.soundings = []  # soundings, rawdata and targets
        
    def get_xml_size(self, buffer):
        asd_file_buffer = buffer[self.start_byte:self.end_byte+1]
        xml_size = xml_size(asd_file_buffer)
        self.xml_size = xml_size
        
    def get_binary_size(self):
        if self.xml_size != 0:
            self.bin_size = self.size - self.xml_size
        else:
            raise RuntimeError('XML size is 0. Please, find xml size first')    
    
    
    @staticmethod
    def create_from_idx_file(path_to_idxfile):
        acf_name, idx_asd = idxfile.read_idx_file(path_to_idxfile)

        asd_objs = []
        
        for idx in idx_asd:
            asd_obj = ASDfile()
            asd_obj.is_grouped_acf = True
            asd_obj.acf_name = acf_name
            
            asd_obj.name = idx.name
            asd_obj.start_byte = idx.start_byte
            asd_obj.end_byte = idx.end_byte
            asd_obj.size = idx.size
            
            asd_objs.append(asd_obj)
            
        return asd_objs

    @staticmethod
    def get_xml_sizes(asd_obj_list, buffer):
        for asd_obj in asd_obj_list:
            asd_obj.get_xml_size(buffer)


# XML datablock parsing

def get_xml_size(buffer):

    buffer = buffer
    loop = True
    xml_size = 0
    # Scan XML length
    while loop:
        try:
            buffer[xml_size:xml_size+1].decode(encoding='utf-8', errors='strict')
        except:
            loop = False
        else:
            xml_size += 1
    
    return xml_size


def get_xml_root(buffer, xml_size):
    xml_string = buffer[:xml_size].decode(encoding='utf-8', errors='strict')
    xml_root = ET.fromstring(xml_string)
    
    return xml_root
    
def parse_xml_header(asd_obj: ASDfile, buffer):
    
    asd_file_buffer = buffer[asd_obj.start_byte:asd_obj.end_byte+1]
    
    xml_size = get_xml_size(asd_file_buffer)
    asd_obj.xml_size = xml_size

    xml_root = get_xml_root(asd_file_buffer, xml_size)
    
    # Parse Basic Info
    basic_dict = xml_root.attrib
    asd_obj.xml_schema = basic_dict['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation']
    asd_obj.system = basic_dict['system']
    asd_obj.cm_version = basic_dict['cmVersion']
    asd_obj.spm_version = basic_dict['spmVersion']
    asd_obj.tbf_version = basic_dict['tbfVersion']
    asd_obj.spmfpga_version = basic_dict['spmFPGAVersion']
    asd_obj.dm80_version = basic_dict['DM80Version']
    asd_obj.doc_daytime = basic_dict['docDaytime']
    asd_obj.no_of_soundings = int(basic_dict['noOfSoundings'])
    asd_obj.reduced_asd = basic_dict['reducedASD']
    
    # Parse Installation
    install_dict = xml_root[0].attrib

    asd_obj.installation.calibrdate = install_dict['calibrDate']
    asd_obj.installation.sysz = float(install_dict['sysZOffset'])
    asd_obj.installation.x = float(install_dict['xOffset'])
    asd_obj.installation.y = float(install_dict['yOffset'])
    asd_obj.installation.z = float(install_dict['zOffset'])
    asd_obj.installation.yaw = float(install_dict['yawOffset'])
    asd_obj.installation.pitch = float(install_dict['pitchOffset'])
    asd_obj.installation.roll = float(install_dict['rollOffset'])
    asd_obj.installation.tx_x = float(install_dict['tx_xOffset'])
    asd_obj.installation.tx_y = float(install_dict['tx_yOffset'])
    asd_obj.installation.tx_z = float(install_dict['tx_zOffset'])
    asd_obj.installation.tx_yaw = float(install_dict['tx_yawOffset'])
    asd_obj.installation.tx_pitch = float(install_dict['tx_pitchOffset'])
    asd_obj.installation.tx_roll = float(install_dict['tx_rollOffset'])   

    # Get AUX Base Time Tag
    asd_obj.aux_base_time = float(xml_root[1].attrib['baseTimeTag']) 
    
    # Parse Motion Data
    motion_dict = xml_root[1][0].attrib
    
    asd_obj.motion.name = motion_dict['name']
    asd_obj.motion.x = float(motion_dict['xOffset'])
    asd_obj.motion.y = float(motion_dict['yOffset'])
    asd_obj.motion.z = float(motion_dict['zOffset'])
    asd_obj.motion.roll = float(motion_dict['rollOffset'])
    asd_obj.motion.pitch = float(motion_dict['pitchOffset'])
    asd_obj.motion.yaw = float(motion_dict['yawOffset'])
    asd_obj.motion.applied_latency = float(motion_dict['appliedLatency'])
    asd_obj.motion.status = float(motion_dict['status'])
    
    motion_qual =  xml_root[1][0][0]
    asd_obj.motion.all_plausible = motion_qual.attrib['allPlausible']
    asd_obj.motion.quality = motion_qual.text.split(' ')
    
    def get_motion_array(root, base_time):
        no_scans = int(root.attrib['noScans'])
        interval = float(root.attrib['scanInterval'])
        start_time_rel2trg = float(root.attrib['startTimeRel2TRG'])
        start_time = base_time + start_time_rel2trg
        
        shape = (no_scans,2)
        data_array = np.ones(shape)
        data_array[:,0] = [float(x) for x in root.text.split(' ') if len(x) != 0]
        data_array[:,1] = [start_time + interval*x for x in np.arange(0,no_scans,1)]
        
        return data_array

    motion_roll = xml_root[1][0][2]
    motion_pitch = xml_root[1][0][3]
    motion_heave = xml_root[1][0][1]
    
    asd_obj.motion.roll = get_motion_array(motion_roll,asd_obj.aux_base_time)
    asd_obj.motion.pitch = get_motion_array(motion_pitch,asd_obj.aux_base_time)
    asd_obj.motion.heave = get_motion_array(motion_heave,asd_obj.aux_base_time)

    # Parse Heading Data:
    def parse_heading(asd_obj: ASDfile, heading_root):
        tg_no = heading_root[0].attrib['noItems']
        qual_no = heading_root[1].attrib['noItems']
        head_no = heading_root[2].attrib['noItems']
        
        if tg_no == qual_no and tg_no == head_no:
            pass
        else:
            RuntimeWarning('Num of tg_no or qual_no and head_no are not equal')
        
        if int(qual_no) == 0:
            asd_obj.heading.all_plausible = heading_root[1].attrib['allPlausible']
        else:
            asd_obj.heading.all_plausible = heading_root[1].attrib['allPlausible']
            asd_obj.heading.quality = [x for x in heading_root[1].text.split(' ') if len(x) != 0]
            
            data_array = np.ones((int(head_no),2))
            data_array[:,0] = [float(x) for x in heading_root[2].text.split(' ') if len(x) != 0]
            data_array[:,1] = [asd_obj.aux_base_time + float(x) for x in heading_root[0].text.split(' ') if len(x) != 0]
            
            asd_obj.heading.heading = data_array
    
    parse_heading(asd_obj, xml_root[1][1])
    
    # Parse Position Data
    def parse_position(asd_obj: ASDfile, pos_root):
        tg_no = pos_root[0].attrib['noItems']
        qual_no = pos_root[1].attrib['noItems']
        lat_no = pos_root[2].attrib['noItems']
        lon_no = pos_root[3].attrib['noItems']
        if tg_no == qual_no and tg_no == lat_no and tg_no == lon_no:
            pass
        else:
            RuntimeWarning('Num some position data_no is not equal')
        
        # parse base info
        asd_obj.position.name = pos_root.attrib['name']
        asd_obj.position.x = float(pos_root.attrib['xOffset'])
        asd_obj.position.y = float(pos_root.attrib['yOffset'])
        asd_obj.position.z = float(pos_root.attrib['zOffset'])
        asd_obj.position.latency = float(pos_root.attrib['latency'])
        asd_obj.position.quality_tag = int(pos_root.attrib['quality'])
        
        if int(qual_no) == 0:
            asd_obj.position.all_plausible = pos_root[1].attrib['allPlausible']
        else:
            # parse data
            asd_obj.position.all_plausible = pos_root[1].attrib['allPlausible']
            asd_obj.position.quality = [x for x in pos_root[1].text.split(' ') if len(x) != 0]
            
            latlon_array = np.ones((int(tg_no),3))
            latlon_array[:,0] = [float(x)*180/np.pi for x in pos_root[2].text.split(' ') if len(x) != 0]
            latlon_array[:,1] = [float(x)*180/np.pi for x in pos_root[3].text.split(' ') if len(x) != 0]
            latlon_array[:,2] = [asd_obj.aux_base_time + float(x) for x in pos_root[0].text.split(' ') if len(x) != 0]
            
            asd_obj.position.latlon = latlon_array
        
    parse_position(asd_obj, xml_root[1][2])
    
    
    def parse_speedcourse(asd_obj, cogsog_root):
        tg_no = cogsog_root[0].attrib['noItems']
        qual_no = cogsog_root[1].attrib['noItems']
        cog_no = cogsog_root[2].attrib['noItems']
        sog_no = cogsog_root[3].attrib['noItems']
        
        if tg_no == qual_no and tg_no == cog_no and tg_no == sog_no:
            pass
        else:
            RuntimeWarning('Num some speed_course data_no is not equal')
        
        # parse base
        asd_obj.speed_course.name = cogsog_root.attrib['name']
        asd_obj.speed_course.x = float(cogsog_root.attrib['xOffset'])
        asd_obj.speed_course.y = float(cogsog_root.attrib['yOffset'])
        asd_obj.speed_course.z = float(cogsog_root.attrib['zOffset'])
        
        if int(qual_no) == 0:
            asd_obj.speed_course.all_plausible = cogsog_root[1].attrib['allPlausible']
        else:
            # parse data
            asd_obj.speed_course.all_plausible = cogsog_root[1].attrib['allPlausible']
            asd_obj.speed_course.quality = [x for x in cogsog_root[1].text.split(' ') if len(x) != 0]
            
            cog_array = np.ones((int(tg_no),2))
            cog_array[:,0] = [float(x) for x in cogsog_root[2].text.split(' ') if len(x) != 0]
            cog_array[:,1] = [asd_obj.aux_base_time + float(x) for x in cogsog_root[0].text.split(' ') if len(x) != 0]
            
            sog_array = np.ones((int(tg_no),2))
            sog_array[:,0] = [float(x) for x in cogsog_root[3].text.split(' ') if len(x) != 0]
            sog_array[:,1] = [asd_obj.aux_base_time + float(x) for x in cogsog_root[0].text.split(' ') if len(x) != 0]
            
            asd_obj.speed_course.cog = cog_array
            asd_obj.speed_course.sog = sog_array
        
    parse_speedcourse(asd_obj, xml_root[1][3])
    
    def parse_depthdata(depthdata_root):
        # parse base
        depth_data_obj = DepthData()
        
        depth_data_obj.name = depthdata_root.attrib['name']
        depth_data_obj.all_plausible = depthdata_root[1].attrib['allPlausible']
        depth_data_obj.quality = [x for x in depthdata_root[1].text.split(' ') if len(x) != 0]
        
        depth_array = np.ones((int(depthdata_root[0].attrib['noItems']), 2))
        depth_array[:,0] = [float(x) for x in depthdata_root[2].text.split(' ') if len(x) != 0]
        depth_array[:,1] = [asd_obj.aux_base_time + float(x) for x in depthdata_root[0].text.split(' ') if len(x) != 0]
        depth_data_obj.depth = depth_array
        
        return depth_data_obj
        
    for depth_root in xml_root[1][4:]:
        if 'depthData' in depth_root.tag:
            depth_obj = parse_depthdata(depth_root)
            asd_obj.depths.append(depth_obj)
            
    # parse PS3 Config
    def parse_ps3config(asd_obj: ASDfile, ps3config_root):
        #parse base:
        asd_obj.ps3config.bo_mode = int(ps3config_root.attrib['boMode'])
        asd_obj.ps3config.bo_mode_name = ps3config_root.attrib['boModeName']
        
        asd_obj.ps3config.ctrl_setting['min'] = ps3config_root[0].attrib['min']
        asd_obj.ps3config.ctrl_setting['max'] = ps3config_root[0].attrib['max']
        asd_obj.ps3config.tracking_mode = ps3config_root[0].attrib['trackingWinMode']
        asd_obj.ps3config.penetration = int(ps3config_root[0].attrib['penetration'])
        
        asd_obj.ps3config.draught = ps3config_root[1].attrib
        asd_obj.ps3config.tx_seq = ps3config_root[2].attrib
        asd_obj.ps3config.src_level = ps3config_root[3].attrib
        asd_obj.ps3config.trg = ps3config_root[4].attrib
        asd_obj.ps3config.pulse_len = ps3config_root[5].attrib
        asd_obj.ps3config.pulse_shape = ps3config_root[6].attrib
        
        asd_obj.ps3config.carrier_freq = ps3config_root[7].attrib
        asd_obj.ps3config.beam_steering = ps3config_root[8].attrib
        
        asd_obj.ps3config.tx_beam_width = ps3config_root[9].attrib
        asd_obj.ps3config.rx_beam_width = ps3config_root[10].attrib
        asd_obj.ps3config.rx_band_width = ps3config_root[11].attrib
        
        asd_obj.ps3config.rx_ampl = ps3config_root[12].attrib
        asd_obj.ps3config.depth_source = ps3config_root[13].attrib
        asd_obj.ps3config.sv_source = ps3config_root[14].attrib
        asd_obj.ps3config.profile_mode = ps3config_root[15].attrib
        asd_obj.ps3config.target_settings = ps3config_root[16].attrib
        
    parse_ps3config(asd_obj, xml_root[2])
    
    # Parse general
    def parse_general(asd_obj: ASDfile, general_root):
        asd_obj.general.sv_mean = float(general_root.attrib['cMean'])
        asd_obj.general.sv_keel = float(general_root.attrib['cKeel'])
        
        asd_obj.general.draught = float(general_root.attrib['draught'])
        asd_obj.general.is_draught_corrected = general_root.attrib['isDraughtCorrected']
        
        asd_obj.general.adc_sample_rate = int(general_root[0].attrib['ADCSampleRate'])
        asd_obj.general.adc_scale_factor = float(general_root[0].attrib['ADCScaleFactor'])
        asd_obj.general.adc_range_min = int(general_root[0].attrib['ADCRangeMin'])
        asd_obj.general.adc_range_max = int(general_root[0].attrib['ADCRangeMax'])
        
        
    parse_general(asd_obj, xml_root[3])
    
    # Parse soundings
    def parse_sounding(sounding_root):
        sounding = Sounding()
        # pulsetarget = PulseTarget()
        
        # Base parsing
        sounding.ident_no = sounding_root.attrib['identNo']
        sounding.datetime = sounding_root.attrib['time']
        sounding.trg_time = float(sounding_root.attrib['timeTRG'])
        sounding.freq_type = sounding_root.attrib['freqType']
        sounding.no_hard_beam = int(sounding_root.attrib['noHardBeams'])
        sounding.no_amplitudes = int(sounding_root.attrib['noAmplitudes'])
        sounding.overdrive = sounding_root.attrib['overdrive']
        
        # Parse Tx Settings
        sounding.tx_no_pulses = int(sounding_root[0].attrib['noPulses'])
        sounding.heave_correction = int(sounding_root[0].attrib['heaveCorrection'])
        sounding.voltage = float(sounding_root[0].attrib['voltage'])
        sounding.duty_cycle = float(sounding_root[0].attrib['dutyCycle'])
        sounding.src_level = float(sounding_root[0].attrib['srcLevel'])
        
        # Parse Pulse
        sounding.pulse_time_rel2trg = float(sounding_root[0][0].attrib['timeRel2TRG'])
        sounding.pulse_len = float(sounding_root[0][0].attrib['length'])
        sounding.pulse_type = sounding_root[0][0].attrib['type']
        sounding.pulse_shape = sounding_root[0][0].attrib['shape']
        sounding.phf_freq = int(sounding_root[0][0].attrib['phf'])
        sounding.slf_freq = int(sounding_root[0][0].attrib['slf'])
        sounding.shf_freq = int(sounding_root[0][0].attrib['shf'])
        
        if 'freqShift' in sounding_root[0][0].attrib.keys():
            sounding.freq_shift = int(sounding_root[0][0].attrib['freqShift'])
        else:
            pass
        sounding.pulse_shading = int(sounding_root[0][0].attrib['shading'])
        sounding.tx_direction = sounding_root[0][0][0].attrib
        
        # Parse Rx
        sounding.rx_signal_car_freq = int(sounding_root[1].attrib['signalCarrierFreq'])
        sounding.rx_gain = float(sounding_root[1].attrib['gain'])
        sounding.rx_sample_rate = float(sounding_root[1].attrib['sampleRate'])
        sounding.rx_bandwidth = int(sounding_root[1].attrib['bandwidth'])
        sounding.rx_spreading = float(sounding_root[1].attrib['spreadingLoss'])
        sounding.rx_absorption = float(sounding_root[1].attrib['absorption'])
        
        # Parse targets
        sounding.tg_no = int(sounding_root[2].attrib['noTargets'])
        sounding.tg_bot_no = int(sounding_root[2].attrib['noBottomTargets'])
        sounding.tg_raytr_no = int(sounding_root[2].attrib['noRayTracedTargets'])
        sounding.tg_raytr_bot_no = int(sounding_root[2].attrib['noRayTracedBottomTargets'])
        
        for target_root in sounding_root[2][:]:
            pulse_target = PulseTarget(
                time=float(target_root.attrib['time']),
                index=int(target_root.attrib['index']),
                pulse_correl=target_root.attrib['pulseCorrelationOn'],
                dist=float(target_root.attrib['dist']),
                type=target_root.attrib['type'],
                ampl=float(target_root.attrib['ampl']),
                ampldB=float(target_root.attrib['ampldB']),
                sn_ratio=float(target_root.attrib['snRatio']),
                classtg=target_root.attrib['class'],
                direction=target_root[0].attrib
            )
            sounding.tg_list.append(pulse_target)
            
        # Parse profiles
        sounding.prof_subident_no = int(sounding_root[3].attrib['subIdentNo'])
        sounding.prof_shading = int(sounding_root[3].attrib['shading'])
        sounding.prof_pulse_no_ref = int(sounding_root[3].attrib['pulseNoRef'])
        sounding.prof_pulse_correl = sounding_root[3].attrib['pulseCorrelationOn']
        sounding.prof_bandwidth = int(sounding_root[3].attrib['bandwidth'])
        sounding.prof_direction = sounding_root[3][0].attrib

        # Parse amplitudes
        sounding.ampl_scan_no = int(sounding_root[3][1].attrib['noScans'])
        sounding.ampl_time_rel2trg = float(sounding_root[3][1].attrib['startTimeRel2TRG'])
        sounding.ampl_scan_interval = float(sounding_root[3][1].attrib['scanInterval'])
        sounding.ampl_notation = sounding_root[3][1].attrib['notation']
        
        return sounding
    
    for root in xml_root[3:]:
        if 'sounding' in root.tag:
            asd_obj.soundings.append(parse_sounding(root))


### Binary datablick parsing

def parse_bin_header(asd_obj: ASDfile, buffer):
    asd_bin_part = buffer[asd_obj.start_byte + asd_obj.xml_size:asd_obj.end_byte+1]
    no_of_soundings = asd_obj.no_of_soundings
    bin_sep = b'\xff\xff\xff\xff'
    
    if len(asd_obj.soundings) == no_of_soundings:
        pass
    else:
        print(asd_obj.soundings)
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
            
            data_array[i, 0] = sample[0]  # Real part
            data_array[i, 1] = sample[1]  # Imag part
            
            buffer_pos = buffer_pos + samp.size
        
        sounding_obj.data_array = data_array
        
        return buffer_pos
    
    buffer_pos = 0
    for sounding in asd_obj.soundings:
        buffer_pos = read_bin_header(buffer_pos, asd_bin_part, sounding)
        buffer_pos = read_bin_data(buffer_pos, asd_bin_part, sounding)

