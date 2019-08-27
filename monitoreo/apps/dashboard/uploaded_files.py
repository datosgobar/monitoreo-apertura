import errno
import os
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile


class PersistentTemporaryUploadedFile(UploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk). The file does
    not delete when closed.
    """
    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        file = tempfile.NamedTemporaryFile(suffix='.upload', dir=settings.MEDIA_ROOT, delete=False)
        super(PersistentTemporaryUploadedFile, self).__init__(file, name, content_type, size, charset, content_type_extra)

    def delete(self):
        return os.remove(self.file.name)

    def temporary_file_path(self):
        """
        Returns the full path of this file.
        """
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except OSError as e:
            if e.errno != errno.ENOENT:
                # Means the file was moved or deleted before the tempfile
                # could unlink it.  Still sets self.file.close_called and
                # calls self.file.file.close() before the exception
                raise
