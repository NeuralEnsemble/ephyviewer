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

#~ import ephyviewer
with open('ephyviewer/version.py') as f:
    version = f.readline()[:-1].split('=')[1].replace(' ', '').replace("'", "")

setup(
    name = "ephyviewer",
    #~ version = ephyviewer.__version__,
    version=version,
    packages = ['ephyviewer', 'ephyviewer.datasource', 'ephyviewer.tests'],
    install_requires=install_requires,
    author = "S.Garcia",
    author_email = "sam.garcia.die@gmail.com",
    description = "Simple viewers for ephy stuff",
    long_description = long_description,
    license = "MIT",
    url='https://github.com/NeuralEnsemble/ephyviewer',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        ]
)
