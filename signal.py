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

def sinusoid(f_sig:     float,
             f_samp:    float,
             t_end:     float,
             shift_rad: float=0):
    """
    Creates a discrete-sampled sinusoid and accompanying array of sample times.

    :param f_sig:       signal frequency
    :param f_samp:      sample frequency
    :param t_end:       end time
    :param shift_rad:   phase shift applied

    :return: t:         iterable (numpy array) of time data points
             sig:       iterable (numpy array) of signal corresponding to t

    TODO: make a little less explicitly coupled to producing time-based data
    """
    n_sig  = t_end*f_sig      # number of cycles
    n_samp = t_end*f_samp + 1 # number of samples
    th  = np.linspace(shift_rad, n_sig*2*np.pi + shift_rad, n_samp)
    t   = np.linspace(0, t_end, n_samp)
    sig = np.sin(th)

    return t, sig
