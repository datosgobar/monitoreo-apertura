from django.core.files.uploadhandler import TemporaryFileUploadHandler

from monitoreo.apps.dashboard.uploaded_files import PersistentTemporaryUploadedFile


class PersistentTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """
    Upload handler that streams data into a temporary file. The temporary file
    must be closed explicitly
    """
    def __init__(self, *args, **kwargs):
        self.file = None
        super(PersistentTemporaryFileUploadHandler, self).__init__(*args, **kwargs)

    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super(PersistentTemporaryFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = PersistentTemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)
