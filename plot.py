import matplotlib.patches
import matplotlib.axis
import matplotlib.axes

def cozero_twins(ax1, ax2):
    # Align on zero.  Make tick/gridlines colinear
    ZOOM_THRESHOLD = .25 # move ratio at which function decides to re-zoom the slave axis to fit both datasets

    def prepend_tick(ticks: list,
                     s:     float):
        """
        Adds a tick to the beginning of the tick list, spaced from the last tick by spacing s

        :param ticks: list of tick locations
        :param s:     spacing between ticks

        :return: None
        """
        ticks.insert(0, ticks[0] - s)

    def append_tick(ticks: list,
                    s:     float):
        """
        Adds a tick to the end of the tick list, spaced from the last tick by spacing s

        :param ticks: list of tick locations
        :param s:     spacing between ticks

        :return: None
        """

        ticks.append(ticks[-1] + s)

    def equalize_ticks(ax1: matplotlib.axes.Axes,
                       ax2: matplotlib.axes.Axes,
                       v:   float):
        """
        Adds a tick to the axis that needs it, to either the lower or upper limit of the axis, as needed.

        :param ax1: axis 1
        :param ax2: axis 2
        :param v:   value to align from both axes

        :return: lists of tick locations on axis 1, axis 2
        """

        t1 = ax1.get_yaxis().get_ticklocs().tolist()
        t2 = ax2.get_yaxis().get_ticklocs().tolist()

        try:
            t1.index(v)
            t2.index(v)
        except ValueError:
            raise ValueError("Value {} not found in one or both axes".format(v))

        # add tick(s) to the axis requiring them:
        while len(t1) - len(t2) < 0:
            # figure out where to add them:
            if tick_relpos(t1, v) > tick_relpos(t2, v):
                append_tick(t1, abs(t1[1] - t1[0]))
            else:
                prepend_tick(t1, abs(t1[1] - t1[0]))
        while len(t2) - len(t1) < 0:
            if tick_relpos(t2, v) > tick_relpos(t1, v):
                append_tick(t2, abs(t2[1] - t2[0]))
            else:
                prepend_tick(t2, abs(t2[1] - t2[0]))

        ax1.get_yaxis().set_ticks(t1)
        ax2.get_yaxis().set_ticks(t2)

        return t1, t2

    def tick_relpos(ticks: list,
                    v:     float):
        """
        Calculates the relative position of the value within the list.

        :param ticks: list of tick locations
        :param v:     value to search for

        :return: float locating the tick specified by v on the interval [0, 1] where 1 is the last tick (100% of
                 axis range) and 0 is the first tick (0% of the axis range)
        """
        return ticks.index(v)/(len(ticks) - 1)

    def detect_extra_ticks(a: matplotlib.axis.Axis):
        """
        Detects the extraneous ticks on an axis, based on the data plotted.

        :param a: axis to check for extraneous ticks

        :return:  tuple of tick indices which could be removed without clipping data
        """
        t = a.get_ticklocs()
        return tuple([i for i in range(len(t) - 1) if t[i+1] < a.get_data_interval()[0]]
                   + [i for i in range(1, len(t)) if t[i-1] > a.get_data_interval()[-1]])

    try:
        ticks1, ticks2 = equalize_ticks(ax1, ax2, 0.0)
    except ValueError:
        return # do nothing if the values to align don't exist in both axes

    # get tick spacing (assumes evenly spaced)
    sp1 = abs(ticks1[1] - ticks1[0])
    sp2 = abs(ticks2[1] - ticks2[0])
    if ticks1.index(0.0) != ticks2.index(0.0):
        # shift ticks to align (if possible without zooming):
        if abs(ticks1.index(0.0) - ticks2.index(0.0))/len(ticks1) <= ZOOM_THRESHOLD:
            while ticks1.index(0.0) < ticks2.index(0.0):
                # prepend to 1, append to 2:
                prepend_tick(ticks1, sp1)
                append_tick(ticks2, sp2)
            while ticks2.index(0.0) < ticks1.index(0.0):
                # prepend to 2, append to 1:
                prepend_tick(ticks2, sp2)
                append_tick(ticks1, sp1)
            # re-tick axes
            ax1.get_yaxis().set_ticks(ticks1)
            ax2.get_yaxis().set_ticks(ticks2)
            cozero_twins(ax1, ax2) # redo with zeros aligned
        # can't shift; rezoom:
        elif ticks2.index(0.0) > ticks1.index(0.0): # need to raise high limit of 2
            lo, hi = ax2.get_ylim()
            ax2.set_ylims(lo, lo + (len(ticks2) + 1) * sp2) # zooms to the equivalent of an additional tick
            cozero_twins(ax1, ax2) # redo process with slight zoom out
        # can't shift; rezoom:
        elif ticks2.index(0.0) < ticks1.index(0.0): # need to lower the low limit of 2
            lo, hi = ax2.get_ylim()
            ax2.set_ylims(hi - (len(ticks2) + 1) * sp2, hi)
            cozero_twins(ax1, ax2) # redo process with slight zoom out

    # trim unnecessary ticks
    to_remove = set(detect_extra_ticks(ax1.get_yaxis())) & set(detect_extra_ticks(ax2.get_yaxis()))
    newticks  = [i for i in range(len(ticks1)) if not i in to_remove]
    t1 = [ticks1[i] for i in newticks]
    t2 = [ticks2[i] for i in newticks]
    ax1.set_ylim((t1[0], t1[-1]))
    ax2.set_ylim((t2[0], t2[-1]))
