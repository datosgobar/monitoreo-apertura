import os
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile


class PersistentTemporaryUploadedFile(TemporaryUploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk). The file does
    not delete when closed.
    """
    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        file = tempfile.NamedTemporaryFile(suffix='.upload', dir=settings.FILE_UPLOAD_TEMP_DIR, delete=False)
        super(PersistentTemporaryUploadedFile, self).__init__(file, name, content_type, size, charset, content_type_extra)

    def delete(self):
        return os.remove(self.file.name)
