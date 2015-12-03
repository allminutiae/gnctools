import numpy as np
import pandas as pd

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
                 ranges:  'iterable of iterables',
                 domain_names: tuple = None,
                 range_names:  tuple = None):
    """
    Interpolates arrays to a common domain, for the extent of the domain given (does not extend beyond the last
    element).

    :param domains:      iterable of iterables; must be monotonically increasing
    :param ranges:       iterable of iterables. NaNs at the ends will result in removal of the NaN as well as the corresponding
                         domain value in the range and domain returned.  NaNs not at the ends will be interpolated to the shared
                         domain.
    :param domain_names: optional list/tuple of names for dictionary output
    :param range_names:  optional list/tuple of names for dictionary output

    :return: tuple of domains, tuple of ranges, or, if domain_names and range_names are provided, dicts of domain and range

    NOTE: if you want to insert points not already in any of the domains, you may submit an extra domain of the points you
          want, with a corresponding range of all NaNs.  The corresponding returned array will be empty but the points
          will be inserted in the shared domain as long as they did not extend the upper or lower bounds of that domain.
    """
    # TODO: fix non removal of leading NaNs in domain return
    # input checks ----------------
    for d, r in zip(domains, ranges):
        assert(len(d)==len(r))
    if not domain_names is None:
        assert(len(domain_names)==len(domains))
    if not range_names is None:
        assert(len(range_names)==len(ranges))
    # -----------------------------

    x_list = [np.squeeze(d) for d in domains]
    x_comb = np.unique(np.concatenate(x_list))

    if not range_names is None:
        colnames = range_names
    else:
        colnames = ['{}'.format(i) for i in range(len(ranges))]

    df = pd.DataFrame(index=x_comb, columns=colnames, dtype=float)
    for d, r, c in zip(domains, ranges, colnames):
        for x, y in zip(d, r):
            df.loc[x, c] = y

    first_ind   = [df[c].first_valid_index() for c in colnames] # this could be the problem; pandas may have changed behavior of first_valid_index()
    rangesisnan = [np.isnan(df[c].values) for c in colnames]
    last_ind    = []
    for r in rangesisnan:
        for isnan, ind in zip(reversed(r), reversed(range(len(r)))):
            if not isnan:
                last_ind.append(ind)
                break

    df         = df.interpolate()
    fullx      = df.index.values
    fullranges = [df[c].values for c in colnames]

    newdomains = tuple([fullx[f:l+1] for f, l in zip(first_ind, last_ind)])
    newranges  = tuple([fr[f:l+1] for fr, f, l in zip(fullranges, first_ind, last_ind)])

    if not domain_names is None and not range_names is None:
        return {n : d for n, d in zip(domain_names, newdomains)}, {n : r for n, r in zip(range_names, newranges)}
    else:
        return newdomains, newranges

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
