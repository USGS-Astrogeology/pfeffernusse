from pfeffernusse.models.isd200 import ISD200

def to_pfeffer_response(data):
    """
    Parse the data into a valid pfeffernusse response
    """
    # Take the flat reponse and create the pfeffernusse obj dicts
    data['detector_center'] = {'line': data['detector_center'][0],
                               'sample': data['detector_center'][1]}

    print(data['sun_velocity'])
    data['sun_velocity'] = {'x': data['sun_velocity'][0],
                            'y': data['sun_velocity'][1],
                            'z': data['sun_velocity'][2]}

    return ISD200.from_dict(data)
    