from re import sub


def to_camel_case(string: str):
    """
    Converts an input string to a camel string.

    :param string: Input string.
    """
    ret = sub(r"(_|-)+", " ", string).title().replace(" ", "")
    return ''.join([ret[0].lower(), ret[1:]])