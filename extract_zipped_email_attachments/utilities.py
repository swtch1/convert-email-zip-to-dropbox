def convert_bytes_to_string(bytes_object):
    """
    Ensure the object passed in is returned as a string.
    :param bytes_object: object to convert
    :return: str
    """
    if isinstance(bytes_object, str):
        return bytes_object
    return bytes_object.decode('utf-8')


def get_unique_dict_keys(dict1, dict2):
    """
    Get the keys that are in one dict but not both.
    :param dict1: 
    :param dict2: 
    :return: set
    """
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    return keys1 - keys2 | keys2 - keys1
