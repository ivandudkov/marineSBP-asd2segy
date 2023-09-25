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
    
class SpeedCourseData:
    def __init__(self) -> None:
        pass

class DepthData:
    def __init__(self) -> None:
        pass
class Installation:
    
    def __init__(self) -> None:
        self.calibrdate = ''  # python dataclass, UTC timezone
        
        # Offsets in m
        self.sys_z = None
        self.sys_x = None
        self.sys_y = None
        self.sys_yaw = None
        self.sys_pitch = None
        self.sys_roll = None
        
        self.tx_x = None
        self.tx_y = None
        self.tx_z = None
        self.tx_yaw = None
        self.tx_pitch = None
        self.tx_roll = None