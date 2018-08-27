from glob import glob
import os

import numpy as np
import pvl
import spiceypy as spice
from pfeffernusse import config

def get_isd(label):

    metakernel_dir = config.mro
    mks = sorted(glob(os.path.join(config.mro,'*.tm')))
    time = label['START_TIME']

    mro_mk = None
    for mk in mks:
        if str(time.year) in os.path.basename(mk):
            mro_mk = mk
    spice.furnsh(mro_mk)

    isd = {}

    instrument_name = label['INSTRUMENT_NAME']
    spacecraft_name = label['SPACECRAFT_NAME']
    target_name = label['TARGET_NAME']

    # Spice likes ids over names, so grab the ids from the names
    spacecraft_id = spice.bods2c('MRO') # Label specifies: MARS_RECONNAISSANCE_ORBITER
    ikid = spice.bods2c('MRO_CTX') # Label specifies: CONTEXT CAMERA

    # Load the instrument and target metadata into the ISD
    reference_frame = 'IAU_{}'.format(target_name)
    
    # Instrument / Spacecraft Metadata
    isd['OPTICAL_DIST_COEF'] = spice.gdpool('INS{}_OD_K'.format(ikid),0, 3)
    isd['ITRANSL'] = spice.gdpool('INS{}_ITRANSL'.format(ikid), 0, 3)
    isd['ITRANSS'] = spice.gdpool('INS{}_ITRANSS'.format(ikid), 0, 3)
    isd['DETECTOR_SAMPLE_ORIGIN'] = spice.gdpool('INS{}_BORESIGHT_SAMPLE'.format(ikid), 0, 1)
    isd['DETECTOR_LINE_ORIGIN'] = spice.gdpool('INS{}_BORESIGHT_LINE'.format(ikid), 0, 1)
    isd['DETECTOR_SAMPLE_SUMMING'] = label['SAMPLING_FACTOR']
    isd['DETECTOR_SAMPLE_SUMMING'] = label['SAMPLING_FACTOR']
    isd['STARTING_SAMPLE'] = label['SAMPLE_FIRST_PIXEL']
    isd['TOTAL_LINES'] = nlines =  label['IMAGE']['LINES']
    isd['TOTAL_SAMPLES'] = spice.gdpool('INS{}_PIXEL_SAMPLES'.format(ikid), 0, 1)
    isd['SENSOR_TYPE'] = 'USGSAstroLineScanner'
    isd['MOUNTING_ANGLES'] = np.zeros(3)
    isd['ISIS_Z_DIRECTION'] = 1
    isd['STARTING_LINE'] = 1.0
    isd['DETECTOR_LINE_OFFSET'] = 0.0
    # Body Parameters
    target_name = label['TARGET_NAME']
    rad = spice.bodvrd(target_name, 'RADII', 3)
    a = rad[1][1]
    b = rad[1][2]
    isd['SEMI_MAJOR_AXIS'] = a * 1000  # Scale to meters
    isd['ECCENTRICITY'] = np.sqrt(1 - (b**2 / a**2)) # Standard eccentricity

    isd['FOCAL'] = spice.gdpool('INS{}_FOCAL_LENGTH'.format(ikid), 0, 1)

    isd['ABERR'] = 0
    isd['ATMREF'] = 0
    isd['PLATFORM'] = 1

    # It really is hard coded this way...
    isd['TRI_PARAMETERS'] = np.zeros(18)
    isd['TRI_PARAMETERS'][15] = isd['FOCAL']

    # Time
    sclock = label['SPACECRAFT_CLOCK_START_COUNT']
    et = spice.scs2e(spacecraft_id, sclock)
    isd['STARTING_EPHEMERIS_TIME'] = et

    half_lines = nlines / 2
    isd['INT_TIME'] = line_rate = label['LINE_EXPOSURE_DURATION'][0] * 0.001  # Scale to seconds
    center_sclock = et + half_lines * line_rate
    isd['CENTER_EPHEMERIS_TIME'] = center_sclock
    isd['SCAN_DURATION'] = line_rate * nlines
    # The socetlinekeywords code is pushing ephemeris and quaternion off of either side of the image.  Therefore,
    # the code needs to know when the start time is.  Since we are not pushing off the edge of the image, the start-time
    # should be identical to the actual image start time.
    isd['T0_QUAT'] = isd['T0_EPHEM'] = isd['STARTING_EPHEMERIS_TIME'] - isd['CENTER_EPHEMERIS_TIME']
    isd['DT_EPHEM'] = 80 * isd['INT_TIME']  # This is every 300 lines

    # Determine how many ephemeris points to compute
    n_ephemeris = int(isd['SCAN_DURATION'] / isd['DT_EPHEM'])
    if n_ephemeris % 2 == 0:
        n_ephemeris += 1
    isd['NUMBER_OF_EPHEM'] = n_ephemeris
    eph = np.empty((n_ephemeris, 3))
    eph_rates = np.empty(eph.shape)
    current_et = et
    for i in range(n_ephemeris):
        loc_direct, _ = spice.spkpos(target_name, current_et, 'IAU_MARS', 'LT+S', 'MRO')
        state, _ = spice.spkezr(target_name, current_et, 'IAU_MARS', 'LT+S', 'MRO')
        eph[i] = loc_direct
        eph_rates[i] = state[3:]
        current_et += isd['DT_EPHEM'] # Increment the time by the number of lines being stepped
    eph *= -1000 # Reverse to be from body center and convert to meters
    eph_rates *= -1000 # Same, reverse and convert
    isd['EPHEM_PTS'] = eph.flatten()
    isd['EPHEM_RATES'] = eph_rates.flatten()

    # Why should / should not the n_quaternions equal the number of ephemeris pts?
    n_quaternions = n_ephemeris
    isd['NUMBER_OF_QUATERNIONS'] = n_quaternions

    isd['DT_QUAT'] = isd['SCAN_DURATION'] / n_quaternions
    qua = np.empty((n_quaternions, 4))
    current_et = et
    for i in range(n_quaternions):
        # Find the rotation matrix
        camera2bodyfixed = spice.pxform('MRO_CTX', 'IAU_MARS', current_et)
        q = spice.m2q(camera2bodyfixed)
        qua[i][:3] = q[1:]
        qua[i][-1] = q[0]
        current_et += isd['DT_QUAT']
    isd['QUATERNIONS'] = qua.flatten()


    # Now the 'optional' stuff
    isd['REFERENCE_HEIGHT'] = label.get('reference_height', 30)
    isd['MIN_VALID_HT'] = label.get('min_valid_height' ,-8000)
    isd['MAX_VALID_HT'] = label.get('max_valid_height', 8000)
    isd['IMAGE_ID'] = label.get('image_id', 'UNKNOWN')
    isd['SENSOR_ID'] = label.get('sensor_id', 'USGS_LINE_SCANNER')
    isd['PLATFORM_ID'] = label.get('platform_id', 'UNKNOWN')
    isd['TRAJ_ID'] = label.get('traj_id', 'UNKNOWN')
    isd['COLL_ID'] = label.get('coll_id', 'UNKNOWN')
    isd['REF_DATE_TIME'] = label.get('ref_date_time', 'UNKNOWN')

    spice.unload(mro_mk)
    
    return isd


