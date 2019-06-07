class Echo:
    """
    An object that implements just the write method of the file-like interface.
    """
    def write(self, value):
        return value
