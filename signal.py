import numpy as np

def asd(data:  'a 1xn (or nx1) numpy.ndarray', # the data to be asd'ed
        fsamp: int):                           # sample frequency
    """
    returns: the amplitude spectral density of the given array, in dB.
             an array of corresponding frequencies
    """

    nsamples  = len(data)

    # find next power of 2 to zero pad for FFT function stability
    targetlen = 1
    while targetlen < nsamples:
        targetlen *= 2

    if targetlen == nsamples:
        padded = data
    else:
        padded = np.resize(data, targetlen)

    ampl    = np.abs(np.fft.rfft(padded))/nsamples*2 # *2 because we're only looking at the + side
    ampl_db = 20.*np.log10(ampl)
    freqs   = np.fft.rfftfreq(targetlen, d=1./fsamp)

    return freqs, ampl_db
