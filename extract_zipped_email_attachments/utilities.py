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
