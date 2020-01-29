import time
import typing
from typing import List

from pathlib import Path
# get the project directory
current_file_path = Path(__file__)
project_dir = Path(__file__).resolve().parents[2]


def get_number_0f_tracks(album_object):
    """ given a spotify album object (full or simplified) returns the number of tracks"""
    return album_object['total_tracks']


def compute_album_length(album_object):
    """This function takes a full album object and returns the
    total album duration in millisecondsd

    parameters: album_object
    returns: integer, length of album
    """
    track_objects = album_object['tracks']['items']
    track_lengths = list(map(lambda obj: obj['duration_ms'], track_objects))
    return sum(track_lengths)