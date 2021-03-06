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

def share_domain(domains: 'iterable of iterables',
                 ranges:  'iterable of np.array'):
    """
    Interpolates arrays to a common domain, for the extent of the domain given (does not extend beyond the last
    element).  Trims datasets such that only the overlapping portion is returned.

    :param domains:      iterable of 1-D arrays; must be monotonically increasing
    :param ranges:       iterable of 1-D arrays

    :return: combined domain, list of ranges

    NOTE:
        - will have an issue with equal-dimensioned arrays (won't be able to distinguish range data entities)
    """
    # TODO: add ability to inject points in domain
    # input checks ----------------
    assert(len(domains) == len(ranges))
    for d, r in zip(domains, ranges):
        assert(is_monotonic(d))
        assert(len(d) in r.shape)
        assert(len(r.shape) <= 2)
    # -----------------------------

    # get floor/ceil of overlapping section, find corresponding indices for each dataset
    x_floor = np.max([np.min(d) for d in domains])
    x_ceil  = np.min([np.max(d) for d in domains])

    # get combined domain points
    x_comb  = np.unique(np.concatenate(domains))
    inds    = np.where(x_floor <= x_comb)
    inds    = np.where(x_ceil  >= x_comb[inds])

    # put in column-array format for slicing up into individual columns:
    newranges = [np.transpose(r) if len(r.shape) > 1 and len(d) == r.shape[1] else r for d, r in zip(domains, ranges)]

    # split out into single columns
    x_list = []
    y_list = []
    dims   = []
    for x, r in zip([np.squeeze(d) for d in domains], newranges):
        if len(r.shape) > 1:
            dims.append(r.shape[1])
            for col in range(r.shape[1]):
                x_list.append(x)
                y_list.append(r[:, col])
        else:
            dims.append(1)
            x_list.append(x)
            y_list.append(r)

    # interpolate to combined domain
    interpranges = [np.interp(x_comb[inds], x, y) for x, y, in zip(x_list, y_list)]

    # need to loop through the interpranges and squish back together based on contents of dims
    finalranges = []
    for dim in dims:
        if dim > 1:
            matrix = []
            for i in range(dim):
                matrix.append(interpranges.pop(0))
            finalranges.append(np.transpose(np.array(matrix))) # will naturally row stack if not specified
        else:
            finalranges.append(np.array(interpranges.pop(0)))

    return x_comb[inds], finalranges

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

def is_monotonic(arr: np.ndarray):
    """
    Returns whether the array given is monotonically increasing or decreasing.  Sections where the values stay the same
    are considered monotonic.

    :param   arr:
    :return: boolean
    """

    dif = np.diff(arr)
    return np.all(dif <= 0.) or np.all(dif >= 0.)

def sanitize_to_iterable(var):
    """
    Takes an iterable or single object and makes it iterable.  If given a dict, returns dict.values().

    :param var:
    :return:
    """
    if isinstance(var, dict):
        variter = var.values()
    else:
        try:
            iter(var)
            variter = var
        except TypeError:
            variter = (var,)

    return variter
