import pandas as pd
import numpy as np
import scipy.io

from collections import Iterable
from os import listdir, mkdir, makedirs
from os.path import isdir, join
from shutil import rmtree, move
from linecache import getline

# TODO: create a unified class which will:
#           allow reading MAT, DAT, CSV, etc
#           allow indexing by column name or column number
#           allow writing to any format
#           facilitate easy plotting/introspection
# TODO: also, make a better "load" function which can figure out what to do on its own

def loadIntoArray(fname:      str,
                  headerline: bool = True,
                  verbose:    bool = True):
    """
    Loads the contents of the file into a numpy.ndarray. Returns the array and header line, if present.
    """
    if verbose:
        print('Loading file ' + fname + ' ...')

    if headerline:
        df = pd.read_csv(filepath_or_buffer = fname,
                         dtype = np.float64,
                         delim_whitespace = True)
        return df.values, df.columns #TODO: this is returning df.columns as an Index object, need to make it just a list
    else:
        df = pd.read_csv(filepath_or_buffer = fname,
                         header = None,
                         dtype = np.float64,
                         delim_whitespace = True)
        return df.values, []

def loadtxt_col(fname:       str,
                col:         'str or iterable of str',
                **kwargs):
    """
    Wraps io.loadtxt, loading only the column(s) of interest.

    :param fname:       filename
    :param col:         the string header of the desired column of data, or a tuple containing the headers for multiple
                        desired columns

    --- kwargs to pass through to loadtxt():
    :param delimiter:   string separator; contiguous whitespace by default
    :param headerlen:   number of rows at the beginning of the file in which to expect a header
    :param commentchar: comment char to strip from beginning of header lines

    :return: an np.array containing the data from column requested

    TODO: add ability to specify column number
    TODO: refactor to save cpu time (maybe using np.loadtxt kwarg 'usecols'), otherwise delete this
    TODO: move this into loadtxt, just add 'col' kwarg
    """

    dat, h = loadtxt(fname, **kwargs)

    if isinstance(col, str):
        if not col in h:
            raise ValueError("The '{}' column requested is not present in {}".format(col, fname))
        else:
            return dat[col]
    elif isinstance(col, Iterable):
        if not set(col).issubset(set(h)):
            raise ValueError("One or more columns requested are not present in {}".format(fname))
        else:
            return tuple([dat[c] for c in col])
    else:
        raise ValueError("Desired column(s) cannot be specified as type {}".format(type(col)))

def loadtxt(fname:       str,
            headerlen:   int  = 1,
            commentchar: str  = '#',
            **kwargs):
    """
    Wraps numpy.loadtxt, returning the data in a dict with the column names as keys.  Assumes single header line by
    default.

    :param   fname:       filename
    :param   headerlen:   number of rows at the beginning of the file in which to expect a header
    :param   commentchar: comment char to strip from beginning of header lines

    -- kwargs:
                delimiter:   string separator; contiguous whitespace by default
                dtype:       data type for np.arrays; float by default

    :return: if rtnheader and headerlen >= 1: see below + list of column headers (2-tuple containing these)

             if headerlen >= 1: a dict with data stored by column name (assumes last line of header has column name info)

             if headerlen == 0: a 2-D array

    """

    dat = np.loadtxt(fname, skiprows=headerlen, **kwargs)

    if 'delimiter' in kwargs.keys():
        delim = kwargs['delimiter']
    else:
        delim = None

    if headerlen >= 1:
        with open(fname) as f:
            for ii, line in enumerate(f):
                if ii == headerlen - 1:
                    break
        headers = [h.strip() for h in line.lstrip(commentchar).split(sep=delim)]
    else:
        headers   = False

    if not headers:
        return dat, None
    else:
        datdict = {h : col for h, col in zip(headers, dat.T)}
        return datdict, headers

def savetxt(fname:    str,
            datadict: dict,
            header:   'ordered iterable of strings' = None):
    """
    Writes an ascii-formatted file with the contents of datadict, in column order by header.

    :param fname:    filename
    :param datadict: dict containing individual columns of data
    :param header:   iterable of header strings; used to specify write order

    TODO: do something smarter if no ordered header provided (i.e., try to locate "time" col, some rudimentary sort)
    """

    if header is None:
        header = datadict.keys()

    data_arr = np.array([datadict[h] for h in header]).T      # transposed because we want data in columns
    headerstr = ''.join(['{:^25}'.format(h) for h in header]) # space pad to default np.savetxt width
    np.savetxt(fname, data_arr, header=headerstr)

def loadmat(fname:     str,
            mdict:     dict = None,
            appendmat: bool = True,
            **kwargs):
    """
    Wrapper function for scipy.io.loadmat which uses numpy.squeeze to remove singular dimensions from arrays
    in the dict returned.  Also returns a np.array if the mat file only contains 1 variable.

    API doc: http://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.io.loadmat.html
    """

    NONDATAKEYS = ('__version__', '__globals__', '__header__')

    mat = scipy.io.loadmat(fname, mdict, appendmat, **kwargs)

    keys = [k for k in mat.keys() if not k in NONDATAKEYS]

    for k in keys:
        mat[k] = np.squeeze(mat[k])

    if len(keys) == 1:
        return mat[keys[0]]
    else:
        return mat

def writeArrayToFile(fname:   str,                 # name & location to save
                     data:    '2D numpy.ndarray',  # matrix of data to write
                     header:  list = (),           # header line
                     verbose: bool = True):
    """
    Writes the contents of the array into the file.
    """

    if verbose:
        print('Writing file ' + fname + ' ...')

    df = pd.DataFrame(data)
    df.to_csv(path_or_buf  = fname,
              sep          = ' ',
              float_format = '%.16e',
              header       = header,
              index        = False)

def makeCleanPath(path: str):
    """
    Creates a clean path at the location specified.  Makes sure the location (1) exists, and
    (2) doesn't have old files in it.  By default, if the directory exists and is not empty,
    creates the sub directory named by the variable PREVDIR in which to store the prior contents.
    It also creates a file WARNFIL with a warning about the fragility of the directory.

    :param   path: the path to be created/emptied
    :return  None

    NOTES:
    ------
    * Useful for quickly making a directory to dump plots, datafiles, etc.
    * PREV directory is for quick oh shit prevention; should not be used in lieu of version control
    """

    PREVDIR = '_@prev'
    WARNFIL = '_@autogen_warning.txt'
    MSG = '''
          WARNING:\n
          This directory and contents were generated by a script which routinely deletes the \n
          contents herein.  Unless version controlled, any data in this directory can be \n
          destroyed forever if the script is re-run.
          '''

    prevdir = join(path, PREVDIR)

    if not isdir(path):
        makedirs(path)
    else:
        ls = set(listdir(path)) # get list of files/dirs
        if isdir(prevdir):
            ls.discard(PREVDIR) # don't include prevdir in move
            rmtree(prevdir)
        mkdir(prevdir)          # make a new empty prevdir
        for name in ls:         # move the old files into prevdir
            move(join(path, name), join(prevdir, name))

    with open(join(path, WARNFIL), 'w') as f:
        f.write(MSG)
