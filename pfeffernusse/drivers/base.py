from abc import ABC, abstractmethod

import spiceypy as spice


class Base(ABC):
    """
    Abstract base class for all PDS label parsing. Implementations should override
    properties where a kernel provider deviates from the most broadly adopted
    approach.

    Methods that must be provided:
    - instrument_id
    - 

    """
    def __init__(self, label, *args, **kwargs):
        self.label = label
    
    def as_dict(self):
        properties = {p:getattr(self, p) for p in dir(self) if not p.startswith('__')}
        return properties


    @property 
    def lines(self):
        return self.label['LINES']

    @property 
    def samples(self):
        return self.label['SAMPLES']
    
    @property
    def target_name(self):
        return self.label['TARGET_NAME']
    
    @property
    def et(self):
        sclock = self.label['SPACECRAFT_CLOCK_START_COUNT']
        exposure_duration = self.label['EXPOSURE_DURATION'].value
        exposure_duration = exposure_duration * 0.001  # Scale to seconds

        # Get the instrument id, and, since this is a framer, set the time to the middle of the exposure
        start_et = spice.scs2e(self.spacecraft_id, sclock)
        start_et += (exposure_duration / 2.0)
        end_et = spice.scs2e(self.spacecraft_id, self.label['SPACECRAFT_CLOCK_STOP_COUNT']) + (exposure_duration / 2.0)
        et = (start_et + end_et)/2
        return et
    
    @property
    def del_et(self):
        sclock = self.label['SPACECRAFT_CLOCK_START_COUNT']
        exposure_duration = self.label['EXPOSURE_DURATION'].value
        exposure_duration = exposure_duration * 0.001  # Scale to seconds

        # Get the instrument id, and, since this is a framer, set the time to the middle of the exposure
        start_et = spice.scs2e(self.spacecraft_id, sclock)
        start_et += (exposure_duration / 2.0)
        end_et = spice.scs2e(self.spacecraft_id, self.label['SPACECRAFT_CLOCK_STOP_COUNT']) + (exposure_duration / 2.0)
        return end_et - start_et

    @property
    def start_et(self):
        sclock = self.label['SPACECRAFT_CLOCK_START_COUNT']
        exposure_duration = self.label['EXPOSURE_DURATION'].value
        exposure_duration = exposure_duration * 0.001  # Scale to seconds

        # Get the instrument id, and, since this is a framer, set the time to the middle of the exposure
        return spice.scs2e(self.spacecraft_id, sclock)
 
    @property
    def spacecraft_name(self):
        return self.label['MISSION_NAME']
    
    @property
    @abstractmethod
    def instrument_id(self):
        pass
    
    @property
    def ikid(self):
        return spice.bods2c(self.instrument_id)

    @property
    def spacecraft_id(self):
        return spice.bods2c(self.spacecraft_name)

    @property 
    def focal2pixel_lines(self):
        return list(spice.gdpool('INS{}_TRANSX'.format(self.ikid), 0, 3))
    
    @property 
    def focal2pixels_samples(self):
        list(spice.gdpool('INS{}_TRANSX'.format(self.ikid), 0, 3))
        
    @property 
    def focal_length(self):
        return float(spice.gdpool('INS{}_FOCAL_LENGTH'.format(self.ikid), 0, 1)[0])
            
    @property 
    def focal_length_epsilon(self):
        return float(spice.gdpool('INS{}_FL_UNCERTAINTY'.format(self.ikid), 0, 1)[0])

    @property
    def starting_detector_line(self):
        return 0
    
    @property
    def starting_detector_sample(self):
        return 0
    
    @property 
    def semimajor(self):
        rad = spice.bodvrd(self.label['TARGET_NAME'], 'RADII', 3)
        return rad[1][1]

    @property
    def semiminor(self):
        rad = spice.bodvrd(self.label['TARGET_NAME'], 'RADII', 3)
        return rad[1][0]

    @property
    def reference_frame(self):
        return 'IAU_{}'.format(self.label['TARGET_NAME'])
    
    @property
    def sun_position(self):
        sun_state, _ = spice.spkezr("SUN",
                                     self.et,
                                     self.reference_frame,
                                     'NONE',
                                     self.label['TARGET_NAME'])

        return sun_state[:4]

    @property
    def sun_velocity(self):
        sun_state, lt = spice.spkezr("SUN",
                                     self.et,
                                     self.reference_frame,
                                     'NONE',
                                     self.label['TARGET_NAME'])

        return sun_state[4:7]
    
    @property
    def sensor_velocity(self):
        vstate, _ = spice.spkezr(self.target_name,
                                           self.et,
                                           self.reference_frame,
                                           'None',
                                           self.label['TARGET_NAME'])
        return vstate[3:6]
    
    @property
    def sensor_position(self):
        loc, _ = spice.spkpos(self.target_name, 
                              self.et, 
                              self.reference_frame, 
                              'None', 
                              self.spacecraft_name)
        return loc[:4]
