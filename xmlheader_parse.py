from dataclasses import dataclass, field

import xml.etree.ElementTree as ET

import asd
import auxillary
    
def xml_size(buffer):

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

def parse_xml_root(asd_obj, xml_root):
    pass



######
filepath = ''


