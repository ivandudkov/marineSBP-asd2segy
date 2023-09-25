from dataclasses import dataclass, field

import xml.etree.ElementTree as ET

import asd
import auxillary
    
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

def parse_xml_header(asd_obj, buffer):
    
    asd_file_buffer = buffer[asd_obj.start_byte:asd_obj.end_byte+1]
    
    xml_size = get_xml_size(asd_file_buffer)
    asd_obj.xml_size = xml_size
    
    xml_root = get_xml_root(asd_file_buffer, xml_size)
    
    return(xml_root)
    
    



