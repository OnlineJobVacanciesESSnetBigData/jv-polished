"""
Most commonly used methods/constants, used across the whole project
"""

import os

# ---------------------------------------------------------------------
# --- Config
# ---------------------------------------------------------------------

ROOT_FOLDER = '/../'  # set where is the root folder of this project, relative of this file
DATA_FOLDER = '/../data/'  # set where is the data folder (storing e.g. outputs from scraping), relative of this file


# ---------------------------------------------------------------------
# --- Commonly used functions
# ---------------------------------------------------------------------

def create_directories_if_necessary(path):
    """
    Given a path, creates all the directories necessary till the last '/' encountered. E.g.

    if '/path/to/' exists and the path argument is '/path/to/file/is/this',
    calling this would create '/path/to/file/is/'
    """

    if '/' not in path:
        return

    dir_path = path[0:path.rfind('/') + 1]

    if os.path.exists(dir_path):
        return

    os.makedirs(dir_path)


def from_root(path, create_if_needed=False):
    """
    Returns path with project root prepended
    """
    proj_root = os.path.realpath(os.path.dirname(__file__)) + ROOT_FOLDER
    result_path = proj_root + path

    if create_if_needed:
        create_directories_if_necessary(result_path)

    return result_path


def from_data_root(path, create_if_needed=False):
    """
    Returns path with data project root prepended
    """
    proj_data_root = os.path.realpath(os.path.dirname(__file__)) + DATA_FOLDER
    result_path = proj_data_root + path

    if create_if_needed:
        create_directories_if_necessary(result_path)

    return result_path




