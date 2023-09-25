import os


class AuxData:
    """Positions, Motions, Depth"""
    
    def __init__(self):
        pass
    

class MotionData:
    
    def __init__(self) -> None:
        
        self.quality_no_items = None
        self.all_plausible = None
        self.heave = None
        self.roll = None
        self.pitch = None
        
class HeadingData:
    
    def __init__(self) -> None:
        pass

class Installation:
    
    def __init__(self) -> None:
        self.calibrdate = ''  # python dataclass, UTC timezone
        
        # Offsets in m
        self.sys_z = '' 
        self.sys_x = ''
        self.sys_y = ''
        self.sys_yaw = ''
        self.sys_pitch = ''
        self.sys_roll = ''
        
        self.tx_x = ''
        self.tx_y = ''
        self.tx_z = ''
        self.tx_yaw = ''
        self.tx_pitch = ''
        self.tx_roll = ''