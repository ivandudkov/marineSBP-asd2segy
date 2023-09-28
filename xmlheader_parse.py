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
        head_no = pos_root[2].attrib['noItems']
        
        if tg_no == qual_no and tg_no == head_no:
            pass
        else:
            RuntimeWarning('Num of tg_no or qual_no and head_no are not equal')
        