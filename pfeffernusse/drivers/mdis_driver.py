from plio.io.io_gdal import GeoDataset
import pvl
from glob import glob
import spiceypy as spice

import os


def get_isd(label, config):
    """
    TODO: This function (and all like it) needs to open with some robust method to make sure this is
          in fact an MDIS label.

    """

    instrument_name = {
        'MDIS-NAC':'MSGR_MDIS_NAC',
        'MERCURY DUAL IMAGING SYSTEM NARROW ANGLE CAMERA':'MSGR_MDIS_NAC',
        'MERCURY DUAL IMAGING SYSTEM WIDE ANGLE CAMERA':'MSGR_MDIS_WAC'
    }


    mks = sorted(glob(config.metakernals_dir+'/*.tm'))

    instrument_id = instrument_name[label['INSTRUMENT_ID']]
    spacecraft_name = label['MISSION_NAME']
    target_name = label['TARGET_NAME']
    time = label['START_TIME']

    messenger_mk = None
    for mk in mks:
        if str(time.year) in os.path.basename(mk):
            messenger_mk = mk

    spice.furnsh(messenger_mk)
    path, tpe, handle, found = spice.kdata(0,'TEXT')

    # Spice likes ids over names, so grab the ids from the names
    spacecraft_id = spice.bods2c(spacecraft_name)
    ikid = spice.bods2c(instrument_id)

    # Load the instrument and target metadata into the ISD
    reference_frame = 'IAU_{}'.format(target_name)

    isd = {}
    # isd['instrument_id'] = instrument_id
    # isd['target_name'] = target_name
    # isd['spacecraft_name'] = spacecraft_id

    rad = spice.bodvrd(target_name, 'RADII', 3)
    isd['semimajor'] = rad[1][0] * 1000
    isd['semiminor'] = rad[1][1] * 1000

    # CSM radial distortion still need some figuring out, for now, pad out to 7 element array
    # By the kernel docs, this array only covers c1, c2, & c4

    # Should work by getting the type of distortion and packaging into the correct object
    # (radial, transverse, guassian whatever-the-fuck)
    isd['optical_distortion'] = {}
    odk_mssgr = spice.gdpool('INS{}_OD_T_Y'.format(ikid),0, 10)
    odk = [0]*5
    odk[1] = odk_mssgr[0]
    odk[2] = odk_mssgr[1]
    odk[4] = odk_mssgr[2]

    isd['optical_distortion']['coefficients'] = odk

    # Jesse needs to look into how to use this key
    isd['optical_distortion']['radial'] = 'radial'

    isd['focal2pixel_samples'] = list(spice.gdpool('INS{}_TRANSX'.format(ikid), 0, 3))
    isd['focal2pixel_lines'] = list(spice.gdpool('INS{}_TRANSY'.format(ikid), 0, 3))

    # Load information from the IK kernel
    isd['focal_length_model'] = {}
    isd['focal_length_model']['focal_length'] = float(spice.gdpool('INS{}_FOCAL_LENGTH'.format(ikid), 0, 1)[0])
    isd['focal_length_model']['focal_length_epsilon'] = float(spice.gdpool('INS{}_FL_UNCERTAINTY'.format(ikid), 0, 1)[0])
    isd['image_lines'] = int(spice.gipool('INS{}_PIXEL_LINES'.format(ikid), 0, 1)[0])
    isd['image_samples'] = int(spice.gipool('INS{}_PIXEL_SAMPLES'.format(ikid), 0, 1)[0])

    try:
        isd['starting_detector_sample'] = int(spice.gdpool('INS{}_FPUBIN_START_SAMPLE'.format(ikid), 0, 1)[0])
    except:
        isd['starting_detector_sample'] = 0
    try:
        isd['starting_detector_line'] = int(spice.gdpool('INS{}_FPUBIN_START_LINE'.format(ikid), 0, 1)[0])
    except:
        isd['starting_detector_line'] = 0

    # Now time
    sclock = label['SPACECRAFT_CLOCK_START_COUNT']
    exposure_duration = label['EXPOSURE_DURATION'].value
    exposure_duration = exposure_duration * 0.001  # Scale to seconds

    # Get the instrument id, and, since this is a framer, set the time to the middle of the exposure
    start_et = spice.scs2e(spacecraft_id, sclock)
    start_et += (exposure_duration / 2.0)

    end_et = spice.scs2e(spacecraft_id, label['SPACECRAFT_CLOCK_STOP_COUNT']) + (exposure_duration / 2.0)
    del_et = end_et - start_et
    et = (start_et + end_et)/2

    isd['starting_ephemeris_time'] = start_et
    isd['dt_ephemeris'] = del_et
    isd['number_of_ephemerides'] = 1
    isd['interpolation_method'] = 'lagrange'
    isd['center_ephemeris_time'] = et

    # Get the rotation angles from MDIS NAC frame to Mercury body-fixed frame
    camera2bodyfixed = spice.pxform(instrument_id, reference_frame, et)
    quat = spice.m2q(camera2bodyfixed)

    isd['sensor_orientation'] = list(quat)

    # Get the Sensor Position
    loc, _ = spice.spkpos(target_name, et, reference_frame, 'LT+S', spacecraft_name)
    loc *= -1000

    isd['sensor_location'] = {}
    isd['sensor_location']['x'] = loc[0]
    isd['sensor_location']['y'] = loc[1]
    isd['sensor_location']['z'] = loc[2]
    isd['sensor_location']['unit'] = 'm'


    # Get the velocity
    v_state, lt = spice.spkezr(spacecraft_name,
                                       et,
                                       reference_frame,
                                       'NONE',
                                       target_name)

    isd['sensor_velocity'] = {}
    isd['sensor_velocity']['x'] = v_state[3] * 1000
    isd['sensor_velocity']['y'] = v_state[4] * 1000
    isd['sensor_velocity']['z'] = v_state[5] * 1000
    isd['sensor_velocity']['unit'] = 'm'
    isd['reference_height'] = {}
    isd['reference_height']['minheight'] = label.get('min_valid_height' ,-8000)
    isd['reference_height']['maxheight'] = label.get('max_valid_height', 8000)
    isd['reference_height']['unit'] = 'KM'


    # Get the sun position
    sun_state, lt = spice.spkezr("SUN",
                                 et,
                                 reference_frame,
                                 'NONE',
                                 target_name)

    # Get the sun position, convert to meters
    xpos, ypos, zpos = [e.value*1000 for e in label['SC_SUN_POSITION_VECTOR']]
    xvel, yvel, zvel = [e.value*1000 for e in label['SC_SUN_VELOCITY_VECTOR']]

    # lighttime should always be off
    isd['sun_position'] = {}
    isd['sun_position']['x'] = sun_state[0] * 1000
    isd['sun_position']['y'] = sun_state[1] * 1000
    isd['sun_position']['z'] = sun_state[2] * 1000

    isd['sun_velocity'] = {}
    isd['sun_velocity']['x'] = sun_state[3] * 1000
    isd['sun_velocity']['y'] = sun_state[4] * 1000
    isd['sun_velocity']['z'] = sun_state[5] * 1000
    return isd
