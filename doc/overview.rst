Overview
========

ephyviewer is a python module for building custuimized viewer
for electrophysiological signals and related stuff (video/events/time frequency...)

I can be used as a stabndalone application just by lauching ot from console::

    ephyviewer
    
    
But th real goal is to design cutumized viewer for your needs::
 
    import ephyviewer
    import numpy as np

    app = ephyviewer.mkQApp()

    #signals
    sigs = np.random.rand(100000,16)
    sample_rate = 1000.
    t_start = 0.
    view1 = ephyviewer.TraceViewer.from_numpy(sigs, sample_rate, t_start, 'Signals')

    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)
    win.add_view(view1)
    win.show()

    app.exec_()

   

    