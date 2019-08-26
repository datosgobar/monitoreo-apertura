import os
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler


class PersistentTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """
    Upload handler that streams data into a temporary file. The temporary file
    must be closed explicitly
    """
    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super(PersistentTemporaryFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = PersistentTemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)


class PersistentTemporaryUploadedFile(TemporaryUploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk). The file does
    not delete when closed.
    """
    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        file = tempfile.NamedTemporaryFile(suffix='.upload', dir=settings.FILE_UPLOAD_TEMP_DIR, delete=False)
        super(TemporaryUploadedFile, self).__init__(file, name, content_type, size, charset, content_type_extra)

    def delete(self):
        return os.remove(self.file.name)
