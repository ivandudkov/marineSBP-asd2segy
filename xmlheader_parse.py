from dataclasses import dataclass, field

import xml.etree.ElementTree as ET
import numpy as np

import asd
from classes_from_xml import DepthData, Sounding, PulseTarget

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

def parse_xml_header2(asd_obj: asd.ASDfile, buffer):
    
    asd_file_buffer = buffer[asd_obj.start_byte:asd_obj.end_byte+1]
    
    xml_size = get_xml_size(asd_file_buffer)
    asd_obj.xml_size = xml_size
    
    xml_root = get_xml_root(asd_file_buffer, xml_size)
    
    return(xml_root)
    
    
def parse_xml_header(asd_obj: asd.ASDfile, buffer):
    
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
    asd_obj.no_of_sounding = int(basic_dict['noOfSoundings'])
    asd_obj.reduced_asd = basic_dict['reducedASD']
    
    # Parse Installation
    install_dict = xml_root[0].attrib

    asd_obj.installation.calibrdate = install_dict['calibrDate']
    asd_obj.installation.sys_x = float(install_dict['xOffset'])
    asd_obj.installation.sys_y = float(install_dict['yOffset'])
    asd_obj.installation.sys_z = float(install_dict['zOffset'])
    asd_obj.installation.sys_yaw = float(install_dict['yawOffset'])
    asd_obj.installation.sys_pitch = float(install_dict['pitchOffset'])
    asd_obj.installation.sys_roll = float(install_dict['rollOffset'])
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
    # newlist = [expression for item in iterable if condition == True]
    
    motion_roll = xml_root[1][0][2]
    motion_pitch = xml_root[1][0][3]
    motion_heave = xml_root[1][0][1]
    
    asd_obj.motion.roll = get_motion_array(motion_roll,asd_obj.aux_base_time)
    asd_obj.motion.pitch = get_motion_array(motion_pitch,asd_obj.aux_base_time)
    asd_obj.motion.heave = get_motion_array(motion_heave,asd_obj.aux_base_time)

    # Parse Heading Data:
    def parse_heading(asd_obj: asd.ASDfile, heading_root):
        tg_no = heading_root[0].attrib['noItems']
        qual_no = heading_root[1].attrib['noItems']
        head_no = heading_root[2].attrib['noItems']
        
        if tg_no == qual_no and tg_no == head_no:
            pass
        else:
            RuntimeWarning('Num of tg_no or qual_no and head_no are not equal')
        
        asd_obj.heading.all_plausible = heading_root[1].attrib['allPlausible']
        asd_obj.heading.quality = [x for x in heading_root[1].text.split(' ') if len(x) != 0]
        
        data_array = np.ones((int(head_no),2))
        data_array[:,0] = [float(x) for x in heading_root[2].text.split(' ') if len(x) != 0]
        data_array[:,1] = [asd_obj.aux_base_time + float(x) for x in heading_root[0].text.split(' ') if len(x) != 0]
        
        asd_obj.heading.heading = data_array
    
    parse_heading(asd_obj, xml_root[1][1])
    
    # Parse Position Data
    def parse_position(asd_obj: asd.ASDfile, pos_root):
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
    def parse_ps3config(asd_obj: asd.ASDfile, ps3config_root):
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
    def parse_general(asd_obj: asd.ASDfile, general_root):
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
        sounding.time_trg = float(sounding_root.attrib['timeTRG'])
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
        sounding.pulse_time = sounding.time_trg + float(sounding_root[0][0].attrib['timeRel2TRG'])
        sounding.pulse_len = float(sounding_root[0][0].attrib['length'])
        sounding.pulse_type = sounding_root[0][0].attrib['type']
        sounding.pulse_shape = sounding_root[0][0].attrib['shape']
        sounding.phf_freq = int(sounding_root[0][0].attrib['phf'])
        sounding.slf_freq = int(sounding_root[0][0].attrib['slf'])
        sounding.shf_freq = int(sounding_root[0][0].attrib['shf'])
        sounding.freq_shift = int(sounding_root[0][0].attrib['freqShift'])
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
        
        
        return sounding
    
    for root in xml_root[3:]:
        if 'sounding' in root.tag:
            asd_obj.soundings.append(parse_sounding(root))