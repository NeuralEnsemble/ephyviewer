# ephyviewer

Simple viewers for ephys signals and related stuff (signal, spikes, events, triggers, video, ...)
Based on PyQt5 (or PyQt4) and pyqtgraph.


Can be use at two level:

## Standalone application 

For file supported by neo.rawio (Axon, Blackrock, BrainVision, Neuralynx,
NeuroExplorer, Plexon, Spike2, Tdt, ...)

Launch it from console and use open menu:
```
ephyviewer
```

Launch it from console with filename (and optional format):
```
ephyviewer File_axon_1.abf
ephyviewer File_axon_1.abf -f Axon
```


## To design some customs viewers for ephy dataset :

With theses kind of codes:

```python

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

```

Doc : http://ephyviewer.readthedocs.io
