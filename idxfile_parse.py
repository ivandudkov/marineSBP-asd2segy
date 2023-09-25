import os

from dataclasses import dataclass, field

@dataclass
class IDXFile():
    name: str
    start_byte: int
    end_byte: int
    size: int
    
def read_idx_file(path):
    idx_files = []
    
    acf_name = os.path.splitext(os.path.basename(path))[0]
    
    with open(path, 'r') as f1:
        f1_content = f1.read().splitlines()
        for line in f1_content:
            lc = line.split()
            
            name =  lc[2]
            start_byte = int(lc[0])
            size = int(lc[1])
            end_byte = start_byte + size - 1
            
            idx_files.append(IDXFile(name=name, start_byte=start_byte, end_byte=end_byte, size=size))
            
    return acf_name, idx_files



