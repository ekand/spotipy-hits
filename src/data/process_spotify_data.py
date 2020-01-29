import statistics

from pathlib import Path
from src.data.pickle_util import load_pickle, save_pickle

# get the project directory
current_file_path = Path(__file__)
project_dir = Path(__file__).resolve().parents[2]


def get_avg_volume(list_of_track_feature_dicts):
    t = []
    for track_feature_dict in list_of_track_feature_dicts:
        try:
            t.append(track_feature_dict['loudness'])
        except TypeError as err:
            print('gentle warning: skipping the None entry for song feature info. error message: \n', err)
    return statistics.mean(t)


def make_dict_of_album_id_to_avg_track_volume(dict_of_album_ids_to_list_of_track_audio_features):
    dict_of_album_id_to_avg_track_volume = {}
    for album_id, list_of_track_audio_features in dict_of_album_ids_to_list_of_track_audio_features.items():
        dict_of_album_id_to_avg_track_volume[album_id] = get_avg_volume(list_of_track_audio_features)

    return dict_of_album_id_to_avg_track_volume


if __name__ == '__main__':
    file_path = str(project_dir) + '/data/raw/dict_of_album_ids_to_list_of_track_audio_features.pickle'
    dict_of_album_ids_to_list_of_track_audio_features = load_pickle(file_path)
    dict_of_album_id_to_avg_track_volume = make_dict_of_album_id_to_avg_track_volume(dict_of_album_ids_to_list_of_track_audio_features)


