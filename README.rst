ephyviewer
==========

*Simple viewers for ephys signals, events, video and more*

:Distributions: |pypi-badge| |anaconda-cloud-badge|
:Source Code:   |github-badge| |conda-forge-feedstock-badge|
:Tests Status:  |github-actions-badge| |conda-forge-azure-badge| |rtd-status-badge| |coveralls-badge|

Documentation_ | `Release Notes`_ | `Issue Tracker`_

**ephyviewer** is a Python library based on pyqtgraph_ for building custom
viewers for electrophysiological signals, video, events, epochs, spike trains,
data tables, and time-frequency representations of signals. It also provides an
epoch encoder for creating annotations.

|screenshot|

**ephyviewer** can be used at two levels: standalone app and library.

For an example of an application that utilizes **ephyviewer**'s capabilities as
a library, see the neurotic_ app and this paper:

    Gill, J. P., Garcia, S., Ting, L. H., Wu, M., & Chiel, H. J. (2020).
    *neurotic*: Neuroscience Tool for Interactive Characterization. eNeuro,
    7(3). https://doi.org/10.1523/ENEURO.0085-20.2020

Standalone application
----------------------

The standalone app works with file types supported by Neo_'s RawIO interface
(Axograph, Axon, Blackrock, BrainVision, Neuralynx, NeuroExplorer, Plexon,
Spike2, Tdt, etc.; see the documentation for neo.rawio_ for the full list).

Launch it from the console and use the menu to select a data file::

    ephyviewer

Alternatively, launch it from the console with a filename (and optionally the
format)::

    ephyviewer File_axon_1.abf
    ephyviewer File_axon_1.abf -f Axon

Library for designing custom viewers for ephys datasets
-------------------------------------------------------

Build viewers using code like this:

.. code:: python

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

Check the docs for more examples_.


.. |pypi-badge| image:: https://img.shields.io/pypi/v/ephyviewer.svg?logo=python&logoColor=white
    :target: pypi_
    :alt: PyPI

.. |anaconda-cloud-badge| image:: https://img.shields.io/conda/vn/conda-forge/ephyviewer.svg?label=anaconda&logo=anaconda&logoColor=white
    :target: anaconda-cloud_
    :alt: Anaconda Cloud

.. |github-badge| image:: https://img.shields.io/badge/github-source_code-blue.svg?logo=github&logoColor=white
    :target: github_
    :alt: GitHub

.. |conda-forge-feedstock-badge| image:: https://img.shields.io/badge/conda--forge-feedstock-blue.svg?logo=conda-forge&logoColor=white
    :target: conda-forge-feedstock_
    :alt: conda-forge Feedstock

.. |github-actions-badge| image:: https://img.shields.io/github/workflow/status/NeuralEnsemble/ephyviewer/tests/master?label=tests&logo=github&logoColor=white
    :target: github-actions_
    :alt: Tests Status

.. |conda-forge-azure-badge| image:: https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/ephyviewer-feedstock?branchName=master
    :target: conda-forge-azure_
    :alt: conda-forge Build Status

.. |rtd-status-badge| image:: https://img.shields.io/readthedocs/ephyviewer/latest.svg?logo=read-the-docs&logoColor=white
    :target: rtd-status_
    :alt: Documentation Status

.. |coveralls-badge| image:: https://coveralls.io/repos/github/NeuralEnsemble/ephyviewer/badge.svg?branch=master
    :target: coveralls_
    :alt: Coverage status

.. |screenshot| image:: https://raw.githubusercontent.com/NeuralEnsemble/ephyviewer/master/doc/img/mixed_viewer_example.png
    :target: https://raw.githubusercontent.com/NeuralEnsemble/ephyviewer/master/doc/img/mixed_viewer_example.png
    :alt: Screenshot

.. _anaconda-cloud:         https://anaconda.org/conda-forge/ephyviewer
.. _conda-forge-azure:      https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=8410&branchName=master
.. _conda-forge-feedstock:  https://github.com/conda-forge/ephyviewer-feedstock
.. _coveralls:              https://coveralls.io/github/NeuralEnsemble/ephyviewer?branch=master
.. _Documentation:          https://ephyviewer.readthedocs.io/en/latest
.. _examples:               https://ephyviewer.readthedocs.io/en/latest/examples.html
.. _github:                 https://github.com/NeuralEnsemble/ephyviewer
.. _github-actions:         https://github.com/NeuralEnsemble/ephyviewer/actions?query=workflow%3Atests
.. _Issue Tracker:          https://github.com/NeuralEnsemble/ephyviewer/issues
.. _Neo:                    https://neo.readthedocs.io/en/latest
.. _neo.rawio:              https://neo.readthedocs.io/en/latest/rawio.html#module-neo.rawio
.. _neurotic:               https://neurotic.readthedocs.io/en/latest
.. _pypi:                   https://pypi.org/project/ephyviewer
.. _pyqtgraph:              http://www.pyqtgraph.org
.. _Release Notes:          https://ephyviewer.readthedocs.io/en/latest/releasenotes.html
.. _rtd-status:             https://readthedocs.org/projects/ephyviewer
