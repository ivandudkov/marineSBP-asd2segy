import os

import idxfile_parse
import xmlheader_parse
from classes_from_xml import Installation, MotionData, HeadingData,\
                             PositionData, SpeedCourseData, DepthData,\
                             PS3Config, GeneralSettings

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
        self.datablock_size = 0
        
        # AUX
        self.installation = Installation()
        self.motion = MotionData()
        self.heading = HeadingData()
        self.position = PositionData()
        self.speed_course = SpeedCourseData()
        self.depths = []
        
        self.ps3config = PS3Config()
        self.general = GeneralSettings()
        
        self.soundings = []  # soundings, rawdata and targets
        
    def get_xml_size(self, buffer):
        asd_file_buffer = buffer[self.start_byte:self.end_byte+1]
        xml_size = xmlheader_parse.xml_size(asd_file_buffer)
        self.xml_size = xml_size
    
    
    @staticmethod
    def create_from_idx_file(path_to_idxfile):
        acf_name, idx_asd = idxfile_parse.read_idx_file(path_to_idxfile)

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