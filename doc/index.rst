**ephyviewer**
==============

*Simple viewers for ephys signals, events, video and more*

.. container::
    :name: badges

    :Distributions: |pypi-badge| |anaconda-cloud-badge|
    :Source Code:   |github-badge| |conda-forge-feedstock-badge|
    :Tests Status:  |github-actions-badge| |conda-forge-azure-badge| |rtd-status-badge| |coveralls-badge|

**Version:** |version| (`other versions`_)

Do you have a large neural/electrophysiological dataset? Do you want to closely
examine the raw signals and other events before performing an in-depth analysis?
Good news! **ephyviewer** is your friend.

**ephyviewer** is both a standalone application and a Python library for
creating scripts that fulfill your visualization needs.

|screenshot|

For an example of an application that utilizes **ephyviewer**'s capabilities as
a library, see the neurotic_ app and this paper:

    Gill, J. P., Garcia, S., Ting, L. H., Wu, M., & Chiel, H. J. (2020).
    *neurotic*: Neuroscience Tool for Interactive Characterization. eNeuro,
    7(3). https://doi.org/10.1523/ENEURO.0085-20.2020

.. _toc:

Table of Contents
-----------------

.. toctree::
    :maxdepth: 2

    overview
    installation
    interface
    examples
    releasenotes


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

.. |screenshot| image:: img/mixed_viewer_example.png
    :alt: Screenshot

.. _anaconda-cloud:         https://anaconda.org/conda-forge/ephyviewer
.. _conda-forge-azure:      https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=8410&branchName=master
.. _conda-forge-feedstock:  https://github.com/conda-forge/ephyviewer-feedstock
.. _coveralls:              https://coveralls.io/github/NeuralEnsemble/ephyviewer?branch=master
.. _github:                 https://github.com/NeuralEnsemble/ephyviewer
.. _github-actions:         https://github.com/NeuralEnsemble/ephyviewer/actions?query=workflow%3Atests
.. _other versions:         https://readthedocs.org/projects/ephyviewer/versions/
.. _pypi:                   https://pypi.org/project/ephyviewer
.. _rtd-status:             https://readthedocs.org/projects/ephyviewer

.. _neurotic:               https://neurotic.readthedocs.io/en/latest
