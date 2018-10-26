from abc import ABC, abstractmethod

from dateutil import parser
import numpy as np
import pvl
import spiceypy as spice

from pfeffernusse.drivers import distortion
from pfeffernusse.models.isd200 import ISD200


class Base(ABC):
    """
    Abstract base class for all PDS label parsing. Implementations should override
    properties where a kernel provider deviates from the most broadly adopted
    approach.

    Methods that must be provided:
    - instrument_id
    - metakernel

    """
    def __init__(self, label, *args, **kwargs):
        self.label = pvl.loads(label)

    def __enter__(self):
        """
        Called when the context is created. This is used
        to get the kernels furnished.
        """
        if self.metakernel:
            spice.furnsh(self.metakernel)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when the context goes out of scope. Once
        this is done, the object is out of scope and the
        kernels can be unloaded.
        """
        spice.unload(self.metakernel)
    
    def to_dict(self):
        return {p:getattr(self, p) for p in dir(self) if not p.startswith('__')}

    def to_pfeffer_response(self):
        """
        Parse the data into a valid pfeffernusse response
        """
        data = self.to_dict()

        # Take the flat reponse and create the pfeffernusse obj dicts
        data['detector_center'] = {'line': data['detector_center'][0],
                                'sample': data['detector_center'][1]}

        # Parse the distortion object out of the 
        if isinstance(self, distortion.RadialDistortion):
            distortion_object = {'radial':{'coefficients':data['odtk']}}
        elif isinstance(self, distortion.TransverseDistortion):
            distortion_object = {'transverse':{'x':data['odtx'],
                                               'y':data['odty']}}
        data['optical_distortion'] = distortion_object

        data['reference_height'] = {'minheight': data['reference_height'][0],
                                    'maxheight': data['reference_height'][1],
                                    'unit': 'm'}

        data['sensor_position'] = {'unit':'m',
                                   'locations':[data['sensor_position']]}

        data['sensor_orientation'] = {'quaternions':[data['sensor_orientation']]}
        
        data['sensor_velocity'] = {'unit':'m',
                                   'velocities': [data['sensor_velocity']]}
        
        data['radii'] = {'semimajor':data['semimajor'],
                         'semiminor':data['semiminor'],
                         'unit': 'm'}

        return ISD200.from_dict(data)
    
    def _compute_ephemerides(self):
        """
        Helper function to pull position and velocity in one pass
        so that the results can then be cached in the associated 
        properties.
        """
        eph = np.empty((self.number_of_ephemerides, 3))
        eph_rates = np.empty(eph.shape)
        current_et = self.starting_ephemeris_time
        for i in range(self.number_of_ephemerides):
            state, _ = spice.spkezr(self.target_name,
                                    current_et,
                                    self.target_name, 
                                    'NONE', 
                                    self.spacecraft_id) # Should this be ikid?
            eph[i] = state[:3]
            eph_rates[i] = state[3:]
            # Increment the time by the number of lines being stepped
            current_et += getattr(self, 'dt_ephemeris', 0)
        eph *= -1000 # Reverse to be from body center and convert to meters
        eph_rates *= -1000 # Same, reverse and convert

        self._sensor_velocity = eph_rates
        self._sensor_position = eph

    @property
    @abstractmethod
    def metakernel(self):
        pass

    @property
    @abstractmethod
    def instrument_id(self):
        pass


    @property
    def start_time(self):
        return self.label['START_TIME']

    @property 
    def image_lines(self):
        return self.label['IMAGE']['LINES']
    
    @property 
    def image_samples(self):
        return self.label['IMAGE']['LINE_SAMPLES']

    @property
    def interpolation_method(self):
        return 'lagrange'

    @property
    def number_of_ephemerides(self):
        return 1

    @property
    def target_name(self):
        return self.label['TARGET_NAME']
    
    @property
    def starting_ephemeris_time(self):
        if not hasattr(self, '_starting_ephemeris_time'):
            sclock = self.label['SPACECRAFT_CLOCK_START_COUNT']
            self._starting_ephemeris_time = spice.scs2e(self.spacecraft_id, sclock)
        return self._starting_ephemeris_time
    
    @property
    def _exposure_duration(self):
        return self.label['EXPOSURE_DURATION'].value * 0.001  # Scale to seconds

    @property
    def ending_ephemeris_time(self):
        if not hasattr(self, '_ending_ephemeris_time'):
            self._ending_ephemeris_time = spice.scs2e(self.spacecraft_id, self.label['SPACECRAFT_CLOCK_STOP_COUNT']) + (self._exposure_duration / 2.0)
        return self._ending_ephemeris_time

    @property
    def center_ephemeris_time(self):
        if not hasattr(self, '_center_ephemeris_time'):
            self._center_ephemeris_time = (self.starting_ephemeris_time + self.ending_ephemeris_time)/2
        return self._center_ephemeris_time

    @property
    def detector_center(self):
        return list(spice.gdpool('INS{}_CCD_CENTER'.format(self.ikid), 0, 2))
 
    @property
    def spacecraft_name(self):
        return self.label['MISSION_NAME']
    
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
    def focal2pixel_samples(self):
        return list(spice.gdpool('INS{}_TRANSX'.format(self.ikid), 0, 3))
        
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
    def detector_sample_summing(self):
        return 1

    @property
    def detector_line_summing(self):
        return self.label.get('SAMPLING_FACTOR', 1)

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
                                     self.center_ephemeris_time,
                                     self.reference_frame,
                                     'NONE',
                                     self.label['TARGET_NAME'])

        return sun_state[:4]

    @property
    def sun_velocity(self):
        sun_state, lt = spice.spkezr("SUN",
                                     self.center_ephemeris_time,
                                     self.reference_frame,
                                     'NONE',
                                     self.label['TARGET_NAME'])

        return sun_state[3:6]
    
    @property
    def sensor_position(self):
        if not hasattr(self, '_sensor_position'):
            self._compute_ephemerides()
        return self._sensor_position.tolist()

    @property
    def sensor_velocity(self):
        if not hasattr(self, '_sensor_velocity'):
            self._compute_ephemerides()
        return self._sensor_velocity.tolist()

    @property
    def sensor_orientation(self):
        if not hasattr(self, '_sensororientation'):
            current_et = self.starting_ephemeris_time
            qua = np.empty((self.number_of_ephemerides, 4))
            for i in range(self.number_of_quaternions):
                # Find the rotation matrix
                camera2bodyfixed = spice.pxform(self.spacecraft_id, 
                                                self.target_name,
                                                current_et)
                q = spice.m2q(camera2bodyfixed)
                qua[i,:3] = q[1:]
                qua[i,3] = q[0]
                current_et += getattr(self, 'dt_quaternion', 0)
            self._sensor_orientation = qua
        return self._sensor_orientation.tolist()

class LineScanner(Base):

    @property
    def _scan_duration(self):
        """
        A constant duration scan rate.
        """
        return self.label['LINE_EXPOSURE_DURATION'][0] * 0.001

    @property
    def line_scan_rate(self):
        """
        In the form: [start_line, line_time, exposure_duration]
        The form below is for a fixed rate line scanner.
        """
        return [self.starting_detector_line, self.start_time, self._scan_duration]

    @property
    def detector_center(self):
        if not hasattr(self, '_detector_center'):
            center_sample = float(spice.gdpool('INS{}_BORESIGHT_SAMPLE'.format(self.ikid), 0, 1)[0])
            center_line = float(spice.gdpool('INS{}_BORESIGHT_LINE'.format(self.ikid), 0, 1)[0])
            self._detector_center = [center_sample, center_line]
        return self._detector_center

    @property
    def center_ephemeris_time(self):
        """
        The center ephemeris time for a fixed rate line scanner.
        """
        if not hasattr(self, '_center_ephemeris_time'):
            halflines = self.image_lines / 2
            center_sclock = self.starting_ephemeris_time + halflines * self._scan_duration
            self._center_ephemeris_time = center_sclock
        return self._center_ephemeris_time

    @property
    def t0_ephemeris(self):
        return self.starting_ephemeris_time - self.center_ephemeris_time
    
    @property
    def t0_quaternion(self):
        return self.starting_ephemeris_time - self.center_ephemeris_time

    @property
    def dt_ephemeris(self):
        return 80 * self._scan_duration
    
    @property
    def number_of_ephemerides(self):
        return int(self._scan_duration / self.dt_ephemeris)
    
    @property 
    def number_of_quaternions(self):
        return int(self._scan_duration / self.dt_quaternion)

    @property
    def dt_quaternion(self):
        return 80 * self._scan_duration

class Framer(Base):
    
    @property
    def number_of_ephemerides(self):
        return 1

    @property
    def number_of_quaternions(self):
        return 1
