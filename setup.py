from setuptools import setup
import os


install_requires = [
                    'numpy',
                    #~ 'PyQt5',
                    'pyqtgraph',
                    'matplotlib',
                    'scipy',
                    ]

long_description = ""

import ephyviewer

setup(
    name = "ephyviewer",
    version = ephyviewer.__version__,
    packages = ['ephyviewer'],
    install_requires=install_requires,
    author = "S.Garcia",
    author_email = "",
    description = "Simple viewers for ephy stuff",
    long_description = long_description,
    license = "MIT",
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        ]
)
