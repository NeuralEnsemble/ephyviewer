# ephyviewer

*Simple viewers for ephys signals, events, video and more*

[![PyPI][pypi-badge]][pypi]
[![Anaconda Cloud][anaconda-cloud-badge]][anaconda-cloud]
[![GitHub][github-badge]][github]
[![conda-forge Feedstock][conda-forge-feedstock-badge]][conda-forge-feedstock]
[![Documentation Status][rtd-status-badge]][rtd-status]

[Documentation] | [Release Notes] | [Issue Tracker]

**ephyviewer** is a Python library based on [pyqtgraph] for building custom
viewers for electrophysiological signals, video, events, epochs, spike trains,
data tables, and time-frequency representations of signals. It also provides an
epoch encoder for creating annotations.

![Screenshot][screenshot]

**ephyviewer** can be used at two levels: standalone app and library.

For an example of an application that utilizes **ephyviewer**'s capabilities as
a library, see the *[neurotic]* app and this paper:

> Gill, J. P., Garcia, S., Ting, L. H., Wu, M., & Chiel, H. J. (2020).
> *neurotic*: Neuroscience Tool for Interactive Characterization. eNeuro,
> 7(3). https://doi.org/10.1523/ENEURO.0085-20.2020

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


[anaconda-cloud]:              https://anaconda.org/conda-forge/ephyviewer
[anaconda-cloud-badge]:        https://img.shields.io/conda/vn/conda-forge/ephyviewer.svg?label=anaconda&logo=anaconda&logoColor=white
[conda-forge-feedstock]:       https://github.com/conda-forge/ephyviewer-feedstock
[conda-forge-feedstock-badge]: https://img.shields.io/badge/conda--forge-feedstock-blue.svg?logo=conda-forge&logoColor=white
[github]:                      https://github.com/NeuralEnsemble/ephyviewer
[github-badge]:                https://img.shields.io/badge/github-source_code-blue.svg?logo=github&logoColor=white
[pypi]:                        https://pypi.org/project/ephyviewer
[pypi-badge]:                  https://img.shields.io/pypi/v/ephyviewer.svg?logo=python&logoColor=white
[rtd-status]:                  https://readthedocs.org/projects/ephyviewer
[rtd-status-badge]:            https://img.shields.io/readthedocs/ephyviewer/latest.svg?logo=read-the-docs&logoColor=white

[Documentation]: https://ephyviewer.readthedocs.io/en/latest/
[Release Notes]: https://ephyviewer.readthedocs.io/en/latest/releasenotes.html
[Issue Tracker]: https://github.com/NeuralEnsemble/ephyviewer/issues

[screenshot]:    https://raw.githubusercontent.com/NeuralEnsemble/ephyviewer/master/doc/img/mixed_viewer_example.png
[pyqtgraph]:     http://www.pyqtgraph.org/
[Neo]:           https://neo.readthedocs.io/en/latest/
[neo.rawio]:     https://neo.readthedocs.io/en/latest/rawio.html#module-neo.rawio
[neurotic]:      https://github.com/jpgill86/neurotic
[examples]:      https://ephyviewer.readthedocs.io/en/latest/examples.html
