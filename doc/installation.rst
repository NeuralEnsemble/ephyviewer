.. _installation:

Installation
============

Requirements:
  * Python ≥ 3.5
  * numpy
  * scipy
  * matplotlib ≥ 2.0
  * pyqtgraph ≥ 0.10.0
  * PySide6, PyQt5, PySide2, or PyQt4 (manual installation required)

Optional dependencies:
  * Neo ≥ 0.6 (standalone app and Neo sources)
  * PyAV (video viewer)
  * pandas (dataframes and CSV writable epoch sources)

To install the latest release::

    pip install ephyviewer

To install the latest development version::

    pip install https://github.com/NeuralEnsemble/ephyviewer/archive/master.zip

To install with conda (``python-neo`` and ``av`` are not strictly required but
are recommended)::

    conda install -c conda-forge ephyviewer python-neo av
