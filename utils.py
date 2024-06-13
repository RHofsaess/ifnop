def get_size(byte: int) -> str:
    """
    Function to convert size format.

    Parameters
    ----------
    byte : int
        bytes to be converted

    Returns
    -------
    str
        size of bytes in a nice format
    """

    for order in ['', 'K', 'M', 'G', 'T', 'P']:
        if byte < 1024:
            return f"{byte:.2f}{order}B"
        byte /= 1024
