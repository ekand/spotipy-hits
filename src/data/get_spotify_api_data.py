import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import dotenv
import os
from pathlib import Path
# import sys

import time
import typing
from typing import List

# get the project directory
current_file_path = Path(__file__)
project_dir = Path(__file__).resolve().parents[2]


def setup_spotify_client():
    dotenv_path = os.path.join(project_dir, '.env')
    dotenv.load_dotenv(dotenv_path)
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp


def clean_rs_album_titles_2020_01_09(titles: List[str]) -> List[str]:
    """
    given a list of titles, makes edits to selected titles
    the purpose is to clean up the names from rolling stone so that
    spotify can find them
    """
    for i, title in enumerate(titles):
        title_clean = title.replace(" - EP", "")
        title_clean = title_clean.replace(", Vol. 2", "")
        title_clean = title_clean.replace("A Star Is Born: Original Motion Picture 2018", "A Star Is Born Soundtrack")
        title_clean = title_clean.replace("Rearview Towns", "Rearview Town")
        title_clean = title_clean.replace("Aladdin: Original Motion Picture Soundtrack 2019", "Aladdin (Original "
                                                                                              "Motion Picture "
                                                                                              "Soundtrack")
        title_clean = title_clean.replace("Quality Control: Control the Streets, Vol. 2", "Quality Control: Control "
                                                                                          "the Streets Volume 2")
        title_clean = title_clean.replace("Port of Miami II", "Port of Miami 2")
        'Port of Miami II'

        titles[i] = title_clean
    return titles


def search_for_albums(titles: List[str], verbose: bool = True):
    """
    Given a list of album titles, returns
    parameters: titles, list of strings
        verbose: boolean, if True the function will print progress
    returns: tuple of searches: a list of results from sp.search()
            and fails: a list of strings with error messages
    """

    sp = setup_spotify_client()
    searches = dict()
    fails = dict()
    for i, title in enumerate(titles):
        time.sleep(1)
        try:
            result = sp.search(title, limit=1, type='album')
            if verbose:
                print(i, title)
            searches[title] = result
            if not result:
                print('null result on ', title)
                fails[title] = 'null result on ' + title

        except BaseException as err:
            print('something went wrong with', title, "error info:", err)
            s = 'something went wrong with ' + title + ", error info: " + err
            fails[title] = s
    return searches, fails


def get_album_name_id_dict(spotipy_album_search_results):
    album_name_id_dict = dict()
    for item_tuple in spotipy_album_search_results.items():
        album_name, albums_pager_object = item_tuple
        try:
            album_object = albums_pager_object['albums']['items'][0]
            album_id = album_object['id']
            album_name_id_dict[album_name] = album_id
        except BaseException as err:
            print('id not found for: ', '     ', album_name)
            print('error:', err)
            print()
    return album_name_id_dict


def get_dict_of_full_album_objects(album_name_id_dict):
    """ returns a dictionary of full spotify album objects
    when given a dictionary with keys being album names
    and values being spotify album ids"""
    sp = setup_spotify_client()
    dict_of_full_album_objects = dict()
    for item_tuple in album_name_id_dict.items():
        album_name, album_id = item_tuple
        full_album_object = sp.album(album_id)
        dict_of_full_album_objects[album_name] = full_album_object
        time.sleep(1)
    return dict_of_full_album_objects


def compute_album_length(album_object):
    """This function takes a full album object and returns the
    total album duration in millisecondsd

    parameters: album_object
    returns: integer, length of album
    """
    track_objects = album_object['tracks']['items']
    track_lengths = list(map(lambda obj: obj['duration_ms'], track_objects))
    return sum(track_lengths)


def get_album_release_date(album_object):
    """This function takes a full album object and returns the release date

    parameters: album_object
    returns: integer, length of album
    """
    return album_object['release date']


def get_dict_of_album_ids_to_list_of_track_audio_features(dict_of_full_spotify_album_objects):
    """
    Given a dict_of_full_spotify_album_objects, ultimately downloads and returns a
    dictionary with keys being album ids and values being lists
    of album feature objects
    """
    # get dict_of_album_ids_and_lists_of_track_ids
    dict_of_album_ids_and_lists_of_track_ids = {}
    for title, album_object in dict_of_full_spotify_album_objects.items():
        album_id = album_object['id']
        dict_of_album_ids_and_lists_of_track_ids[album_id] = []
        for simplified_track_object in album_object['tracks']['items']:
            track_id = simplified_track_object['id']
            dict_of_album_ids_and_lists_of_track_ids[album_id].append(track_id)

    # setup spotify client
    sp = setup_spotify_client()

    # using dict_of_album_ids_and_lists_of_track_ids, query spotify
    # and get a dict_of_album_ids_and_lists_of_track_audio_feature_objects
    dict_of_album_ids_and_lists_of_track_audio_feature_objects = {}
    for album_id, list_of_track_ids in dict_of_album_ids_and_lists_of_track_ids.items():
        dict_of_album_ids_and_lists_of_track_audio_feature_objects[album_id] = []
        try:
            assert len(list_of_track_ids) <= 50  # spotify api only accepts 50 tracks per request
            dict_of_album_ids_and_lists_of_track_audio_feature_objects[album_id] = sp.audio_features(list_of_track_ids)
            time.sleep(0.25)
        except AssertionError:
            portions = []
            for i in range(len(list_of_track_ids) // 50 + 1):  # split the api requests into batches
                portions.append(list_of_track_ids[i * 50: (i + 1) * 50])
            for portion in portions:
                dict_of_album_ids_and_lists_of_track_audio_feature_objects[album_id].append(sp.audio_features(portion))
                time.sleep(0.25)
    return dict_of_album_ids_and_lists_of_track_audio_feature_objects


if __name__ == '__main__':
    import pickle_util
    # file_path = str(project_dir) + '/data/raw/' + 'dict_of_full_spotify_album_objects_rs_200_year_2019.pickle'
    # dict_of_full_spotify_album_objects = pickle_util.load_pickle(file_path)
    #
    # dict_of_album_ids_to_list_of_track_audio_features = get_dict_of_album_ids_to_list_of_track_audio_features(dict_of_full_spotify_album_objects)
    # file_path = str(project_dir) + '/data/raw/' + 'dict_of_album_ids_to_list_of_track_audio_features.pickle'
    # pickle_util.save_pickle(dict_of_album_ids_to_list_of_track_audio_features, file_path)

    sp = setup_spotify_client()
    response = sp.album('4i3rAwPw7Ln2YrKDusaWyT')
    sp.search(q='i,i', limit=1, type='album')
