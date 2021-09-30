from io import StringIO
from typing import Protocol


class CorporateEventsFileStorage(Protocol):
    """Corporate events Files storage"""

    def download(self, file: str) -> str:
        """Download file from Storage and returns the path to the downloaded file"""

    def upload(self, buffer: StringIO, file_name: str):
        """Uploads the buffer to storage and save it with the file_name"""

    def move_to_archive(self, file_name: str):
        """Archive the file in the archive directory in storage"""

    def move_to_unprocessed(self):
        """Moves the file to the unprocessed directory"""
