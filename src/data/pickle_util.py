import pickle
import os


def save_pickle(data, file_path):
    assert not os.path.exists(file_path), "file already exists, write operation canceled"
    with open(file_path, 'wb') as outfile:
        pickle.dump(data, outfile)


def load_pickle(file_path):
    with open(file_path, 'rb') as infile:
        return pickle.load(infile)
