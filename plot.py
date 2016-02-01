import matplotlib.pyplot as plt
import matplotlib.patches
from itertools import product
from geohagan.util import sanitize_to_iterable
from matplotlib.font_manager import FontProperties

# TODO: clean up this module--there's lots of stuff that doesn't even need to be here anymore (size/appearance
#       tweaks etc that I know the API well enough for now)
def align_yvalues(ax1, v1, ax2, v2):
    """
    Adjusts ax2 y limits such that v2 is aligned with v1.

    :param ax1:
    :param v1:
    :param ax2:
    :param v2:
    :return:
    """

    miny, maxy = ax2.get_ylim() # current y lims

    _, y1 = ax1.transData.transform((0, v1)) # transforming v1 to display coords
    _, y2 = ax2.transData.transform((0, v2)) # transforming v2 to display coords
    adjust_yaxis(ax2, (y1 - y2) / 2, v2)
    adjust_yaxis(ax1, (y2 - y1) / 2, v1)

def adjust_yaxis(ax, ydiff, v):
    """
    Shifts the y axis by ydiff, maintaining v at the same location.

    :param ax:
    :param ydif:
    :param v:
    :return:
    """
    # TODO: need to add code to check the major ticks and round lims up to the next major tick
    # TODO: secondary axis isn't getting optimal zoom, just whatever works; need to add an argument to hint, I think

    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydiff))
    miny, maxy = ax.get_ylim()
    miny, maxy = miny - v, maxy - v
    if -miny>maxy or (-miny==maxy and dy > 0):
        nminy = miny
        nmaxy = miny*(maxy+dy)/(miny+dy)
    else:
        nmaxy = maxy
        nminy = maxy*(miny+dy)/(maxy+dy)
    ax.set_ylim(nminy+v, nmaxy+v)

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

def embiggen_font():
    fp = FontProperties()
    fp.set_size('20')
    fp.set_weight('normal')
    fp.set_family('sans-serif')

def subplot_grid(rowkeys  : tuple,
                 colkeys  : tuple,
                 titles   : tuple = None,
                 xlabels  : tuple = None,
                 ylabels  : tuple = None,
                 suptitle : str   = None,
                 xlim     : tuple = None,
                 grid     : bool  = True):
    """
    Returns a dict of subplot axes sharing x axis by column and y axis by row, indexed by rowkeys and colkeys.

    :param rowkeys:  row keys for returned dict
    :param colkeys:  column keys for returned dict
    :param titles:   title for each column
    :param xlabels:
    :param ylabels:
    :param suptitle: supertitle; title of the whole group of subplots
    :return:
    """
    # TODO: add xlim
    # TODO: add ability to not specify 2nd axis of keys when only a row/column of plots is needed

    embiggen_font()

    if not titles:  titles  = ['' for col in colkeys]
    if not xlabels: xlabels = ['' for col in colkeys]
    if not ylabels: ylabels = ['' for row in rowkeys]

    assert(len(colkeys)==len(titles)==len(xlabels))
    assert(len(rowkeys)==len(ylabels))

    fig      = plt.figure(figsize=(20.5, 10.5), dpi=92) # good for my screen
    axes     = {}
    firstrow = rowkeys[0]
    firstcol = colkeys[0]
    lastrow  = rowkeys[-1]
    lastcol  = colkeys[-1]
    for ii, (row, col) in enumerate(product(rowkeys, colkeys)):
        if row == firstrow and col == firstcol:
            axes[row, col] = fig.add_subplot(len(rowkeys), len(colkeys), ii+1) # top left subplot is independent
        elif row == firstrow:
            axes[row, col] = fig.add_subplot(len(rowkeys), len(colkeys), ii+1, sharey=axes[firstrow, firstcol]) # first row only share y axis
        elif col == firstcol:
            axes[row, col] = fig.add_subplot(len(rowkeys), len(colkeys), ii+1, sharex=axes[firstrow, firstcol]) # first col only share x axis
        else:
            axes[row, col] = fig.add_subplot(len(rowkeys), len(colkeys), ii+1, sharex=axes[firstrow, col], sharey=axes[row, firstcol]) # all others share x, y with col, row respectively

    # title columns, add x labels
    for col, title, xlab in zip(colkeys, titles, xlabels):
        axes[firstrow, col].set_title(title, fontsize=14)
        axes[rowkeys[-1], col].set_xlabel(xlab)

    # add y labels, add y tick labels on far right if necessary
    for row, ylab in zip(rowkeys, ylabels):
        axes[row, firstcol].set_ylabel(ylab)
        if len(colkeys) > 1:
            axes[row, lastcol].yaxis.tick_right()

    # hide redundant x and y tick labels
    for row, col in product(rowkeys, colkeys):
        if row != lastrow: hide_xticklabels(axes[row, col])
        if col != firstcol and col != lastcol: hide_yticklabels(axes[row, col])

    subplot_spacing = {'bottom' : 0.075,
                       'right'  : 0.95,
                       'left'   : 0.075,
                       'top'    : 0.95,
                       'wspace' : 0.075,
                       'hspace' : 0.1}

    # allow room for suptitle
    if (isinstance(suptitle, bool) and suptitle == True) or isinstance(suptitle, str): subplot_spacing['top'] = .9
    if isinstance(suptitle, str): plt.suptitle(suptitle, fontsize=22)

    fig.subplots_adjust(**subplot_spacing)

    if grid: add_grid(axes.values())

    if not xlim is None: set_xlim(axes, xlim)

    return fig, axes

def add_grid(axes : 'single axes or dict/iterable of axes'):

    axesiterable = sanitize_to_iterable(axes)

    for a in axesiterable:
        a.grid(b=True, which='major', linestyle='-', color=(.7, .7, .7))
        a.grid(b=True, which='minor')

    return axes

def add_legend(axes     : 'iterable or single axes object',
               colors   : tuple,
               styles   : tuple,
               names    : tuple,
               loc      : str    = 'best',
               fancybox : bool   = True,
               **kwargs):
    """
    Convenience function to create a legend according to input parameters and add it to the axes or figure object(s) given.

    :param axes:     single axes or figure object or iterable
    :param colors:   iterable of colors for lines (or patches) in legend
    :param styles:   iterable of linestyles for lines or patches in legend (to specify patch, use 'patch')
    :param names:    iterable of line/patch labels for legend
    :param loc:      location string (defaults to 'best')
    :param fancybox: rounded corners (default True)

    :return: a legend object created according to input parameters
    """
    # TODO get rid of sanitizing a dict to dict.values(); just require iterable
    # TODO make this return an iterable if passed an iterable

    assert(len(colors)==len(styles)==len(names))
    legend = None
    axesiterable = sanitize_to_iterable(axes)

    fp       = FontProperties()
    origsize = fp.get_size()
    fp.set_size('small')

    lines = []
    for c, s in zip(colors, styles):
        if s == 'patch':
            lines.append(matplotlib.patches.Patch(color=c))
        else:
            lines.append(plt.Line2D(range(10), range(10), color=c, linestyle=s))

    for a in axesiterable: legend = a.legend(lines, names, loc=loc, fancybox=fancybox, **kwargs)

    fp.set_size(origsize) # re-set font size

    return legend

def hide_xticklabels(axes : 'iterable or single axes object'):
    axesiterable = sanitize_to_iterable(axes)

    for a in axesiterable:
        for label in a.get_xticklabels():
            label.set_visible(False)

def hide_yticklabels(axes : 'iterable or single axes object'):
    axesiterable = sanitize_to_iterable(axes)

    for a in axesiterable:
        for label in axes.get_yticklabels():
            label.set_visible(False)

def set_logx(axes):
    axesiterable = sanitize_to_iterable(axes)

    for a in axesiterable:
        a.set_xscale('log')

def set_xlim(axes,
             lims: tuple):

    assert(len(lims)==2)
    assert([isinstance(l, float) or isinstance(l, int) for l in lims])

    axesiterable = sanitize_to_iterable(axes)

    for a in axesiterable:
        a.set_xlim(lims)

def set_ylim(axes,
             lims: tuple):

    assert(len(lims)==2)
    assert([isinstance(l, float) or isinstance(l, int) for l in lims])

    axesiterable = sanitize_to_iterable(axes)

    for a in axesiterable:
        a.set_ylim(lims)

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