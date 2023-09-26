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


class PS3Config:
    """Parastore config part"""
    
    def __init__(self) -> None:
        self.bo_mode = int()  # bo for boat?
        self.bo_mode_name = str()
        self.ctrl_setting = {'min': int(), 'max': int()}
        self.tracking_mode = str()
        self.penetration = int()
        
        self.draught = {'source': str()}
        self.tx_seq = {'mode': str()}
        self.src_level = {'mode': str(), 'tx_power_man': float()}
        self.trg = {'trg_mode': str()}
        self.pulse_len = {'mode': str(), 'length_man': float()}  # pulse length in sec?
        self.pulse_shape = {'mode': str()}
        
        self.carrier_freq = {'req_phf': int(), 'req_slf': int()}
        self.beam_steering = {'mode': str(), 'roll_steer': float(), 'pitch_steer': float()}
        self.tx_beam_width = {'mode': str()}
        self.rx_beam_width = {'mode': str()}
        self.rx_band_width = {'mode': str()}
        
        self.rx_ampl = {'mode': str(), 'gain': float(), 'gain_shift': float()}  # receiver amplification
        self.depth_source = str()
        self.sv_source = {'c_keel': str(), 'c_mean': str()}
        self.profile_mode = str()
        self.target_settings = {'wc_targets_on': str(), 'pulse_correlation_on': str(), 
                                'target_tpe_sel': str(), 'target_tpe_on': str(), 
                                'target_tpe_limit': int()}
        
        
class GeneralSettings:
    """C(sv)-mean, C(sv)-keel, analogue-digital converter (ADC) settings"""
    
    def __init__(self) -> None:
        self.sv_mean = float()
        self.sv_keel = float()
        
        self.draught = float()
        self.is_draught_corrected = bool()
        
        self.adc_sample_rate = int()
        self.adc_scale_factor = float()
        self.adc_range_min = int()
        self.adc_range_max = int()
        

class Sounding:
    
    def __init__(self) -> None:
        self.ident_no = int()
        self.datetime = datetime.datetime()  # UTC timezone
        self.time_trg = float()  # POSIX time reference tag. self.datetime and self.time_trg the same
        # it is preferrable to use time trg, because it has .6f sec precision, while datetime has time up to secs
        
        self.freq_type = str()
        self.no_hard_beam = int()
        self.no_amplitudes = int()
        self.overdrive = bool()
        
        # Tx Settings
        self.tx_no_pulses = int()
        self.heave_correction = int()
        
        self.voltage = float()
        self.duty_cycle = float()
        self.src_level = float()
        
        self.pulse_time = float()
        self.pulse_len = float()
        self.pulse_type = str()
        self.pulse_shape = str()
        self.phf = int()
        self.slf = int()
        self.shf = int()
        self.freq_shift = int()
        self.pulse_shading = int()
        self.tx_direction = {'abs':bool(), 'n':float(), 'e': float(), 'd': float()}  # northing, easting, d??
        
        # Rx Settings
        self.rx_signal_car_freq = int()
        self.rx_gain = int()
        self.rx_sample_rate = float()
        self.rx_bandwidth = int()
        self.rx_spreading = float()
        self.rx_absorption = float()
        
        
        
        