import numpy as np
from dataclasses import dataclass, field

class Installation:
    
    def __init__(self) -> None:
        self.calibrdate = ''  # python dataclass, UTC timezone
        
        self.sysz = float()  # the height in [m] of the systems ref point above the ship's keel
        # Offsets, m
        self.z = float()  # positive downward
        self.x = float()  # positive bow
        self.y = float()  # positive starboard
        self.yaw = float()  # positive if turned to starboard
        self.pitch = float()  # positive if bow is up
        self.roll = float()  # positive if starboard is down
        
        self.tx_x = float()  # positive downward
        self.tx_y = float()  # positive bow
        self.tx_z = float()  # positive starboard
        self.tx_yaw = float()
        self.tx_pitch = float()
        self.tx_roll = float() 
        
class MotionData:
    
    def __init__(self) -> None:
        self.name = str()
        
        # Offsets
        self.z = float()
        self.x = float()
        self.y = float()
        self.yaw = float()
        self.pitch = float()
        self.roll = float()
        
        self.applied_latency = float()
        self.status = float()
        
        self.all_plausible = bool()
        self.quality = list()
        
        self.heave = np.empty((2,1))  # m
        self.roll = np.empty((2,1))  # rad
        self.pitch = np.empty((2,1))  # rad
        
class HeadingData:
    
    def __init__(self) -> None:
        self.all_plausible = bool()
        self.quality = list()
        
        self.heading = np.empty((2,1))  # deg or rad???

class PositionData:
    
    def __init__(self) -> None:
        self.name = str()
        
        # Offsets, m
        self.z = float()
        self.x = float()
        self.y = float()
        self.latency = float()
        self.quality_tag = int()

        self.all_plausible = bool()
        self.quality = list()
        
        self.latlon = np.empty((2,1))

class SpeedCourseData:
    
    def __init__(self) -> None:
        self.name = str()
        
        # Offsets, m
        self.z = float()
        self.x = float()
        self.y = float()

        self.all_plausible = bool()
        self.quality = list()
        
        self.cog = np.empty((2,1))  # course over ground, deg?
        self.sog = np.empty((2,1))  # speed over ground, knots
        
class DepthData:
    def __init__(self) -> None:
        self.name = str()
        
        self.all_plausible = bool()
        self.quality = list()
        
        self.depth = np.empty((2,1))  # m


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
        
        self.rx_ampl = {'mode': 'manual', 'gain': '0.000000', 'gainShift': '00.000000'}  # receiver amplification
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
        self.ident_no = str()
        self.datetime = ''  # UTC timezone
        self.trg_time = float()  # POSIX time reference tag. self.datetime and self.time_trg the same
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
        
        self.pulse_time_rel2trg = float()
        self.pulse_len = float()
        self.pulse_type = str()
        self.pulse_shape = str()
        self.phf_freq = int()
        self.slf_freq = int()
        self.shf_freq = int()
        self.freq_shift = int()
        self.pulse_shading = int()
        self.tx_direction = {'abs':bool(), 'n':float(), 'e': float(), 'd': float()}  # northing, easting, d??
        
        # Rx Settings
        self.rx_signal_car_freq = int()
        self.rx_gain = float()
        self.rx_sample_rate = float()
        self.rx_bandwidth = int()
        self.rx_spreading = float()
        self.rx_absorption = float()
        
        # PulseTargets
        self.tg_no = int()
        self.tg_bot_no = int()
        self.tg_raytr_no = int()
        self.tg_raytr_bot_no = int()
        self.tg_list = []
        
        # PulseProfiles
        self.prof_subident_no = int()
        self.prof_shading = bool()
        self.prof_pulse_no_ref = int()
        self.prof_pulse_correl = bool()
        self.prof_bandwidth = int()
        self.prof_direction = {'abs':bool(), 'n':float(), 'e': float(), 'd': float()}  # north, east, down
        
        # Amplitudes info
        self.ampl_scan_no = int()  # same as Sample No
        self.ampl_time_rel2trg = float()
        self.ampl_scan_interval = float()  # sample interval in secs
        self.ampl_notation = str()
        
        # Binary Header
        self.bh_sep = bytes()
        self.bh_len = int()
        self.bh_bytes_per_sample = int()
        self.bh_sample_no = int()  # same as Scan No
        self.bh_head_ver = str()
        self.bh_data_type = str()
        self.bh_ident_num = int()
        self.bh_subident_num = int()
        self.bh_flag = int()
        
        # Binary Data
        self.data_array = np.ones((1,2)) # 0 - real part, 1 - imag part
        
    
@dataclass    
class PulseTarget:
    time: float  # Posix time // The absolute time the target is related with. In [s] since 1 Jan 1970
    index: int  
    pulse_correl: str  # Is true, if target detection algorythmhas applied a pulse correlation
    dist: float  # Distance to target expressed in sound traveltime (two way)
    type: str  # Type of the target ['BOTTOM', 'NON-BOTTOM']
    ampl: float  # Target echo amplitude in [V]
    ampldB: float  # Same as 'ampl' but this amplitude is given in [dB] related to 2.5 V as 0 dB
    sn_ratio: float  # Associated signal-to-noise ratio
    classtg: str  # quality classifier of the target
    direction: dict  # target direction
        
        
        