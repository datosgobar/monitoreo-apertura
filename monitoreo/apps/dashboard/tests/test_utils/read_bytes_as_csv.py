import csv
from io import StringIO


def read_content_as_csv(_bytearray):
    reader = csv.reader(StringIO(_bytearray.decode('utf-8')))
    return reader
