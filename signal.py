import numpy as np

def psd(data:  'a 1xn (or nx1) numpy.ndarray', # the data to be asd'ed
        fsamp: int):                           # sample frequency
    """
    returns: the power spectral density of the given array, in dB.
             an array of corresponding frequencies

    NOTE: this algorithm mirrors the "periodogram" function in Matlab, but
          with the addition of zero-padding to the nearest power of 2 for fft
          function stability.

          source: http://www.mathworks.com/help/signal/ug/psd-estimate-using-fft.html
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

    psdx   = np.power(np.abs(np.fft.rfft(padded)), 2)/nsamples/fsamp
    psdx[1:-1] = psdx[1:-1]*2
    psd_db = 10.*np.log10(psdx)
    freqs  = np.fft.rfftfreq(targetlen, d=1./fsamp)

    return freqs, psd_db
