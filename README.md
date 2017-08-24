# ephyviewer

Simple viewers for ephys signals and related stuff (signal, spikes, events, triggers, video, ...)
Based on PyQt5 and pyqtgraph.


Can be use at two level:

# standalone application to open file supported by neo.rawio

launch from console:
```
ephyviewer
```



# To script in python some customs viewers for dataset with theses kind of codes:

```pyhton
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