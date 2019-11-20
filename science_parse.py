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
from datadiff import diff
from diff_match_patch import diff_match_patch
from strsimpy.normalized_levenshtein import NormalizedLevenshtein


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


def pdf_diff(
        file1_path: str,
        file2_path: str
        ) -> dict:
    """
    Generates a diff between two PDF files.

    Both files will be parsed through science-parse and then a diff will be
    build on their metadata and content.

    Example:
        pdf_diff(path_to_pdf_1, path_to_pdf_2)

    Args:
        file1_path (str): The path to the first PDF file.
        file2_path (str): The path to the second PDF file.

    Returns:
        dict: The gen
    """

    # Parse the files.
    parsed_file1 = parse(open(file1_path, 'rb'))
    parsed_file2 = parse(open(file2_path, 'rb'))

    # Use simple data diff for everything but for the sections.
    sections_old = parsed_file1['sections']
    sections_new = parsed_file2['sections']
    del parsed_file1['sections']
    del parsed_file2['sections']

    metadata_diff = diff(parsed_file1, parsed_file2)

    sections_diff = list()
    sections_new_matched_indexes = list()

    old_section_index = 0
    for old_section in sections_old:
        new_section_index = match_section(old_section_index, old_section, sections_new)

        # If the old section cannot be matched to one of the sections in the
        # new list, then threat it like a deleted one, by simulating emtpy
        # strings for the heading and the text.
        if (new_section_index == None):
            new_section = {'heading': '', 'text': ''}
        else:
            new_section = sections_new[new_section_index]
            sections_new_matched_indexes.append(sections_new_matched_indexes)

        section_diff = {}
        dmp = diff_match_patch()
        section_diff['heading'] = dmp.diff_main(old_section['heading'], new_section['heading'])
        section_diff['text'] = dmp.diff_main(old_section['text'], new_section['text'])

        sections_diff.append(section_diff)

        old_section_index += 1

    # Sections that have not been matched must be new.
    new_section_index = 0
    for new_section in sections_new:
        if (new_section_index not in sections_new_matched_indexes):
            old_section = {'heading': '', 'text': ''}
            
            section_diff = {}
            dmp = diff_match_patch()
            section_diff['heading'] = dmp.diff_main(old_section['heading'], new_section['heading'])
            section_diff['text'] = dmp.diff_main(old_section['text'], new_section['text'])

            sections_diff.append(section_diff)

    return {'metadata': metadata_diff.diffs, 'sections': sections_diff}


def match_section(
            previous_index: int,
            previous_section: dict,
            current_sections: list
            ) -> int:
    """
    Matches an old section version to a newer one in a list of sections.

    Args:
        previous_index (int): The previous index of the section in the list.
        previous_section (dict): The previous version of the section.
        current_sections (list): The current sections list.

    Returns:
        int: The position of the new section version in the sections list. -1,
        if not a statisticaly significant match has been found.
    """
    matched_section_index = None

    # Easiest match against the section at the same position.
    if (previous_index < len(current_sections)):
        new_section = current_sections[previous_index]
        # If the headings match then it is safe to assume that the section 
        # position did not change.
        if (previous_section['heading'] == new_section['heading']):
            matched_section_index = previous_index
            return matched_section_index
        else:
            match_score = compare_text(previous_section['text'], new_section['text'])
            # If the text is identical to at least 50 % then this is most 
            # probably the right section.
            if (match_score >= 0.5):
                matched_section_index = previous_index
                return matched_section_index
        
        # If couldn't match the previous section at its original index then 
        # search through all new sections for the best match. 
        new_section_index = 0
        highest_score = 0
        highest_score_index = 0
        # todo how to deal with 2 matched sections with the same score?
        for new_section in current_sections:
            match_score = compare_text(previous_section['text'], new_section['text'])
            if (match_score > highest_score):
                highest_score = match_score
                highest_score_index = new_section_index

            new_section_index += 1

        return highest_score_index

def compare_text(
            text1: str,
            text2: str
            ) -> float:
    """
    Compares two texts and returns their match percentage.
    
    Args:
        text1 (str): The first text.
        text2 (str): The second text.
    
    Returns:
        float: The match percentage.
    """
    # other methods described at 
    # https://github.com/luozhouyang/python-string-similarity
    normalized_levenshtein = NormalizedLevenshtein()
    distance = normalized_levenshtein.distance(text1, text2)
    return distance
