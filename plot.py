import matplotlib.pyplot as plt

def fullscreen_subplots(*args, **kwargs):
    """
    Sets up full-screen subplot axes that are usually good for my screen (YMMV) and for saving to file.
    Just wraps plt.subplots(), applies custom subplot spacing, and tells fig manager to show maximized.
    """
    # TODO: refactor the fullscreen-ness and adjustments into individual decorators instead of tweaking here

    subplot_spacing = {'bottom' : 0.075,
                       'right'  : 0.95,
                       'left'   : 0.075,
                       'top'    : 0.95,
                       'wspace' : 0.05,
                       'hspace' : 0.075}

    fig, ax = plt.subplots(*args, **kwargs)
    fig.subplots_adjust(**subplot_spacing)
    plt.get_current_fig_manager().window.showMaximized()

    return fig, ax

def bode(freq:  'numpy array-like',
         gain:  'numpy array-like',
         phase: 'numpy array-like',
         axes:  'array/list/tuple of matplotlib supblot axes' = None,
         **kwargs):
    """
    Does a bode plot.  If no axes are provided, creates own axes via the bodeSetup() function.

    kwargs:
        title    -- str, plot title
        xlim     -- tuple (or other sequence) to denote x axis limits
        gainlim  -- tuple (or other sequence) to denote gain y axis limits
        phaselim -- tuple (or other sequence) to denote phase y axis limits

    returns:
        figure -- matplotlib.figure object
        axes   -- numpy.ndarray of matplotlib.axis._subplot.SubplotAxes (2 elements)
    """
    # TODO: move the grid setup (and axis hiding, ticks, etc) into a setup function

    if not axes:
        fig, axes = fullscreen_subplots(2, 1, sharex=True)

    gainlim = kwargs.get('gainlim', None)
    phaselim = kwargs.get('phaselim', None)
    title = kwargs.get('title', None)
    xlim = kwargs.get('xlim', None)

    axes[0].plot(freq, gain)
    if gainlim: axes[0].set_ylim(gainlim)
    if title: axes[0].set_title(title)
    axes[0].set_ylabel('Gain (dB)')

    axes[1].plot(freq, phase)
    if phaselim: axes[1].set_ylim(phaselim)
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Phase (deg)')

    for a in axes:
        a.set_xscale('log')
        if xlim: a.set_xlim(xlim)
        # gridlines
        a.grid(b=True, which='major', linestyle='-', color=(.6, .6, .6))
        a.grid(b=True, which='minor')
        # hide axes borders
        a.spines['top'].set_visible(False)
        # hide ticks too
        a.xaxis.set_ticks_position('bottom')

    return axes[0].figure, axes