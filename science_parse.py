"""
Wrapper for the science-parse API exposed by an science-parse server
found at https://github.com/allenai/science-parse.

To use this wrapper a server must be hosted. Therefore follow the guide
at https://github.com/allenai/science-parse/blob/master/server/README.md
"""

from typing import Optional, BinaryIO
import json
from enum import Enum
import requests
import sys


URL = 'http://localhost:8080/v1'
HEADERS = {
    'Content-Type': 'application/pdf'
}


class Format(Enum):
    """Return formats offered by the science-parse server"""
    LABELED_DATA = 'LabeledData'
    EXTRACTED_METADATA = 'ExtractedMetadata'


def parse(
        file_: BinaryIO,
        format_: Optional[Format] = Format.LABELED_DATA,
        url: str = URL
        ) -> dict:
    """
    Parse a pdf file and output its parsed content as a dict.

    Example:

        parse(open('file.pdf', 'rb'), format_=Format.EXTRACTED_METADATA)

    Arguments:
        file_: File which should be parsed
        format_: Format which the server should return
        server: URL of the server which hosts the science-parse API
        port: Port of the server which hosts the science-parse API
    """
    url = f'{url}?format={format_.value}'
    response = requests.post(url, data=file_, headers=HEADERS)
    return json.loads(response.content)

