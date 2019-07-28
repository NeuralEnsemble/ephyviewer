# ephyviewer

[![Documentation Status][docs-badge]](https://ephyviewer.readthedocs.io/en/latest/?badge=latest)

**ephyviewer** is a Python library based on [pyqtgraph] for building custom
viewers for electrophysiological signals, video, events, epochs, spike trains,
data tables, and time-frequency representations of signals. It also provides an
epoch encoder for creating annotations.

![Screenshot][screenshot]

**ephyviewer** can be used at two levels: standalone app and library.

## Standalone application

The standalone app works with file types supported by [Neo]'s RawIO interface
(Axograph, Axon, Blackrock, BrainVision, Neuralynx, NeuroExplorer, Plexon,
Spike2, Tdt, etc.; see the documentation for [neo.rawio] for the full list).

Launch it from the console and use the menu to select a data file:
```
ephyviewer
```

Alternatively, launch it from the console with a filename (and optionally the
format):
```
ephyviewer File_axon_1.abf
ephyviewer File_axon_1.abf -f Axon
```

## Library for designing custom viewers for ephys datasets

Build viewers using code like this:

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

Check the docs for more [examples].


[docs-badge]: https://readthedocs.org/projects/ephyviewer/badge/?version=latest
[screenshot]: https://raw.githubusercontent.com/NeuralEnsemble/ephyviewer/master/doc/img/mixed_viewer_example.png
[pyqtgraph]:  http://www.pyqtgraph.org/
[Neo]:        https://neo.readthedocs.io/en/latest/
[neo.rawio]:  https://neo.readthedocs.io/en/latest/rawio.html#module-neo.rawio
[examples]:   https://ephyviewer.readthedocs.io/en/latest/examples.html
