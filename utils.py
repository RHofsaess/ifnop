def get_size(bytes: int) -> str:
    """
    Function to convert size format.

    Parameters
    ----------
    bytes : int
        bytes to be converted

    Returns
    -------
    str
        size of bytes in a nice format
    """

    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


# Plotting