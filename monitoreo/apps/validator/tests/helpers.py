import os


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


def catalog_path(file_name):
    return os.path.join(SAMPLES_DIR, file_name)


def open_catalog(file_name):
    return open(catalog_path(file_name), 'rb')
