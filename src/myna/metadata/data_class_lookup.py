""" Lookup data for common name to object name"""


def return_data_class_name(data_name, build=None, part=None):
    data_class_lookup = {
        "spot_size": "SpotSize",
        "laser_power": "LaserPower",
        "material": "Material",
        "preheat": "Preheat",
        "scanpath": "Scanpath",
        "stl": "STL",
        "layer_thickness": "LayerThickness",
    }
    try:
        data_class_name = data_class_lookup[data_name]
    except KeyError as e:
        print(e)
        print("ERROR: Data name is not valid. Valid data names:")
        for key in data_class_lookup.keys():
            print(f"    - {key}")
        exit()
    return data_class_name