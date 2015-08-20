import numpy as np

from os import chdir, getcwd, remove
from os.path import abspath
from shutil import copy, move
from subprocess import call
from scipy.io import savemat

def runExe(exe_name:  str,
           exe_dir:   str,
           pre_copy:  dict,
           post_move: dict):
    """
    Function to handle running an executable.  Copies files into new locations, moves output files.

    :param exe_name:  filename of executable (not path)
    :param exe_dir:   path to the directory in which the executable resides
    :param pre_copy:  dict of files to copy prior to run (keys paths get copied to values paths)
    :param post_move: dict of files to move after run (keys paths get moved to values paths)
    :return:
    """
    #Copies files in pre_copy, cds to exe_dir, runs exe_name, moves files in post_move.

    # convert paths to absolute
    this_dir = abspath(getcwd())
    exe_dir  = abspath(exe_dir)

    # copy input files
    for key, value in pre_copy.items():
        copy(key, value)

    # change directories, run code, change back
    chdir(exe_dir)
    print('Running ' + exe_name + '...')
    call(exe_name)
    chdir(this_dir)
    print('Finished! \n')

    # move output files
    for key, value in post_move.items():
        move(key, value)

def convertToMAT(path_old:     str,
                 path_new:     str,
                 includecols:  tuple = None,
                 delete_orig:  bool  = False):
    """
    Converts a given table file to MAT file format.  Stores the contents as nx1 arrays by header names.

    :param path_old:    path to the ascii-formatted file
    :param path_new:    path to the new, MAT-formatted file
    :param includecols: if not None, used to specify which columns in the file to include
    :param delete_orig: delete the old file
    :return: nothing
    """
    # TODO: add some parsing to map common column names to a standard formatted set (i.e. "Time" "time (s)" etc.)
    # TODO: add more "unit cleansing" stuff

    with open(path_old, 'r') as f:
        lines = list(f)
        hdr   = lines.pop(0).split()                                          # remove header line, split by whitespace
        hdr   = [h for h in hdr if h != '(ft/s)' and h != '(deg/s)']          # clean units stuff
        # TODO: make above only take header items for which data exists
        if includecols is None: includecols = [ii for ii in range(len(hdr))]  # make includecols include all if not specified
        arrays = [np.empty((len(lines)), dtype=float) for col in includecols] # make list of preallocated arrays
        for row, line in enumerate(lines):
            words = line.split()                        # break line into tokens
            for array, col in zip(arrays, includecols): # loop through include cols
                array[row] = float(words[col])          # put values in array

    data = {hdr[col] : np.squeeze(array) for col, array in zip(includecols, arrays)}

    savemat(path_new, data)

    if delete_orig:
        remove(path_old)