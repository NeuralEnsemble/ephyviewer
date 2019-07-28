.. _overview:

Overview
========

ephyviewer is a Python library for building custom viewers for
electrophysiological signals, video, events, epochs, spike trains, data tables,
and time-frequency representations of signals. It also provides an epoch encoder
for creating annotations.

ephyviewer can be used as a standalone application (requires Neo_ ≥ 0.6) by
launching it from the console, then using the menu to open a data file::

    ephyviewer

See the documentation for :mod:`neo.rawio` for available formats.

You can skip the file menu by specifying a filename from the console (and
optionally the format, though this can usually be detected automatically)::

    ephyviewer File_axon_1.abf
    ephyviewer File_axon_1.abf -f Axon

However, where ephyviewer really shines is as a library for designing custom
viewers in simple Python scripts that meet your individual needs::

    import ephyviewer
    import numpy as np

    app = ephyviewer.mkQApp()

    # create example signals
    sigs = np.random.rand(100000,16)

    # create a viewer for the signals
    sample_rate = 1000.
    t_start = 0.
    view1 = ephyviewer.TraceViewer.from_numpy(sigs, sample_rate, t_start, 'Signals')

    # create a window
    win = ephyviewer.MainViewer()
    win.add_view(view1)
    win.show()

    # launch the app
    app.exec_()

Have a look at the :ref:`examples` to see how to create both simple and
sophisticated viewers, and at the :ref:`interface` guide for how to use the
interface.


.. _Neo:        https://neo.readthedocs.io/en/latest/
