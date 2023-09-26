import os
import datetime
import numpy as np


class Installation:
    
    def __init__(self) -> None:
        self.calibrdate = datetime.datetime()  # python dataclass, UTC timezone
        
        # Offsets, m
        self.sys_z = float()
        self.sys_x = float()
        self.sys_y = float()
        self.sys_yaw = float()
        self.sys_pitch = float()
        self.sys_roll = float()
        
        self.tx_x = float()
        self.tx_y = float()
        self.tx_z = float()
        self.tx_yaw = float()
        self.tx_pitch = float()
        self.tx_roll = float()

class AuxData:
    """Positions, Motions, Depth"""
    
    def __init__(self):
        basetime_tag = ''  # posix-time
        
        motion_data = []
        heading_data = []
        position_data = []
        speedcourse_data = []
        depth_data = []  
        
class MotionData:
    
    def __init__(self) -> None:
        self.name = str()
        
        # Offsets
        self.z = float()
        self.x = float()
        self.y = float()
        self.yaw = float()
        self.sys_pitch = float()
        self.sys_roll = float()
        
        self.applied_latency = float()
        self.status = float()
        
        self.all_plausible = bool()
        self.quality_plausible = list()
        
        self.heave = np.array()  # m
        self.roll = np.array()  # rad
        self.pitch = np.array()  # rad
        
class HeadingData:
    
    def __init__(self) -> None:
        self.all_plausible = bool()
        self.quality_plausible = list()
        
        self.heading = np.array()  # deg or rad???

class PositionData:
    
    def __init__(self) -> None:
        self.name = str()
        
        # Offsets, m
        self.z = float()
        self.x = float()
        self.y = float()
        self.latency = float()
        self.quality = int()

        self.all_plausible = bool()
        self.quality_plausible = list()
        
        self.lat = np.array()
        self.lon = np.array()

class SpeedCourseData:
    
    def __init__(self) -> None:
        self.name = str()
        
        # Offsets, m
        self.z = float()
        self.x = float()
        self.y = float()

        self.all_plausible = bool()
        self.quality_plausible = list()
        
        self.cog = np.array()  # course over ground, deg?
        self.sog = np.array()  # speed over ground, knots
        
class DepthData:
    def __init__(self) -> None:
        self.name = str()
        
        self.all_plausible = bool()
        self.quality_plausible = list()
        
        self.depth = np.array()  # m

