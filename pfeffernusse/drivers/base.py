from abc import ABC, abstractmethod

from dateutil import parser
import spiceypy as spice

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
        self.label = label

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
        return parser.parse(self.label['START_TIME'])

    @property 
    def image_lines(self):
        return self.label['LINES']

    @property
    def interpolation_method(self):
        return 'lagrange'

    @property
    def number_of_ephemerides(self):
        return 1

    @property 
    def image_samples(self):
        return self.label['SAMPLES']
    
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
    def ending_ephemeris_time(self):
        if not hasattr(self, '_ending_ephemeris_time'):
            exposure_duration = self.label['EXPOSURE_DURATION'].value
            exposure_duration = exposure_duration * 0.001  # Scale to seconds
            self._ending_ephemeris_time = spice.scs2e(self.spacecraft_id, self.label['SPACECRAFT_CLOCK_STOP_COUNT']) + (exposure_duration / 2.0)
        return self._ending_ephemeris_time

    @property
    def center_ephemeris_time(self):
        if not hasattr(self, '_center_ephemeris_time'):
            self._et = (self.starting_ephemeris_time + self.ending_ephemeris_time)/2
        return self._center_ephemeris_time

    @property
    def dt_ephemeris(self):
        if not hasattr(self, '_dt_ephemeris'):
            self._dt_ephemeris = self.ending_ephemeris_time - self.starting_ephemeris_time 
        return self._dt_ephemeris

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
        return 0

    @property
    def detector_line_summing(self):
        return self.label.get(['SAMPLING_FACTOR'], None)

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

class LineScanner(Base):
    def to_pfeffer_response(self):
        """
        Parse the data into a valid pfeffernusse response
        """
        data = self.to_dict()

        # Take the flat reponse and create the pfeffernusse obj dicts
        data['detector_center'] = {'line': data['detector_center'][0],
                                'sample': data['detector_center'][1]}

        data['sun_velocity'] = [{'x': data['sun_velocity'][0],
                                'y': data['sun_velocity'][1],
                                'z': data['sun_velocity'][2]}]

        data['sensor_velocity'] = [{'x' : data['sensor_velocity'][0],
                                   'y' : data['sensor_velocity'][1],
                                   'z' : data['sensor_velocity'][2]}]

        data['sun_position'] = [{'x' : data['sun_position'][0],
                                'y' : data['sun_position'][1],
                                'z' : data['sun_position'][2]}]

        data['reference_height'] = {'minheight': data['reference_height'][0],
                                    'maxheight': data['reference_height'][1]}

        return ISD200.from_dict(data)

    @property
    def sensor_velocity(self):
        vstate, _ = spice.spkezr(self.target_name,
                                           self.center_ephemeris_time,
                                           self.reference_frame,
                                           'None',
                                           self.label['TARGET_NAME'])
        return vstate[3:6]
    
    @property
    def sensor_position(self):
        loc, _ = spice.spkpos(self.target_name, 
                              self.center_ephemeris_time, 
                              self.reference_frame, 
                              'None', 
                              self.spacecraft_name)
        return loc[:4]

    @property
    def sensor_orientation(self):
        camera2bodyfixed = spice.pxform(self.instrument_id,
                                        self.target_name,
                                        self.center_ephemeris_time)
        q = spice.m2q(camera2bodyfixed)
        # Reorder the quaternion
        return [q[1], q[2], q[3], q[0]]

    @property
    def line_scan_rate(self):
        """
        In the form: [start_line, line_time, exposure_duration]
        The form below is for a fixed rate line scanner.
        """
        return [self.start_line, self.start_time, self.exposure_duration]

    @property
    def _scan_duration(self):
        """
        A constant duration scan rate.
        """
        return self.label['LINE_EXPOSURE_DURATION'][0] * 0.001

    @property
    def detector_center(self):
        if not hasattr(self, '_detector_center'):
            center_sample = float(spice.gdpool('INS{}_BORESIGHT_SAMPLE'.format(self.ikid), 0, 1))
            center_line = float(spice.gdpool('INS{}_BORESIGHT_LINE'.format(self.ikid), 0, 1))
            self._detector_center = [center_sample, center_line]
        return self._detector_center

    @property
    def center_ephemeris_time(self):
        """
        The center ephemeris time for a fixed rate line scanner.
        """
        if not hasattr(self, '_center_ephemeris_time'):
            halflines = self.image_lines / 2
            center_sclock = self.starting_ephemeris_time + halflines * self.scan_duration
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
        return 80 * self.scan_duration
    
    @property
    def number_of_ephemerides(self):
        return int(self.scan_duration / self.dt_ephemeris)

    @property
    def dt_quaternion(self):
        pass

    @property
    def sensor_position(self):
        if not hasattr(self, '_sensor_position'):
            self._compute_ephemerides()
        return self._sensor_position

    @property
    def sensor_velocity(self):
        if not hasattr(self, '_sensor_velocity'):
            self._compute_ephemerides()
        return self._sensor_velocity

    @property 
    def number_of_quaternions(self):
        return int(self.scan_duration / self.dt_quaternion)

    @property
    def dt_quaternion(self):
        return 80 * self.scan_duration

    @property
    def sensor_orientation(self):
        if not hasattr(self, '_sensororientation'):
            current_et = self.starting_ephemeris_time
            for i in range(self.number_of_quaternions):
                # Find the rotation matrix
                camera2bodyfixed = spice.pxform(self.spacecraft_id, 
                                                self.target,
                                                current_et)
                q = spice.m2q(camera2bodyfixed)
                qua[i,:3] = q[1:]
                qua[i,3] = q[0]
                current_et += self.dt_quaternion
            self._sensor_orientation = qua.flatten()
        return self._sensor_orientation

    def _compute_ephemerides(self):
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
            current_et += self.dt_ephemeris # Increment the time by the number of lines being stepped
        eph *= -1000 # Reverse to be from body center and convert to meters
        eph_rates *= -1000 # Same, reverse and convert

        self._sensor_velocity = eph_rates
        self._sensor_position = eph

class Framer(Base):
    def to_pfeffer_response(self):
        """
        Parse the data into a valid pfeffernusse response
        """
        data = self.to_dict()

        # Take the flat reponse and create the pfeffernusse obj dicts
        data['detector_center'] = {'line': data['detector_center'][0],
                                'sample': data['detector_center'][1]}

        data['sun_velocity'] = [{'x': data['sun_velocity'][0],
                                'y': data['sun_velocity'][1],
                                'z': data['sun_velocity'][2]}]

        data['sensor_velocity'] = [{'x' : data['sensor_velocity'][0],
                                   'y' : data['sensor_velocity'][1],
                                   'z' : data['sensor_velocity'][2]}]

        data['sun_position'] = [{'x' : data['sun_position'][0],
                                'y' : data['sun_position'][1],
                                'z' : data['sun_position'][2]}]

        data['reference_height'] = {'minheight': data['reference_height'][0],
                                    'maxheight': data['reference_height'][1]}

        return ISD200.from_dict(data)

    @property
    def sensor_velocity(self):
        vstate, _ = spice.spkezr(self.target_name,
                                           self.center_ephemeris_time,
                                           self.reference_frame,
                                           'None',
                                           self.label['TARGET_NAME'])
        return vstate[3:6]
    
    @property
    def sensor_position(self):
        loc, _ = spice.spkpos(self.target_name, 
                              self.center_ephemeris_time, 
                              self.reference_frame, 
                              'None', 
                              self.spacecraft_name)
        return loc[:4]

    @property
    def sensor_orientation(self):
        camera2bodyfixed = spice.pxform(self.instrument_id,
                                        self.target_name,
                                        self.center_ephemeris_time)
        q = spice.m2q(camera2bodyfixed)
        # Reorder the quaternion
        return [q[1], q[2], q[3], q[0]]