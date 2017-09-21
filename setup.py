from setuptools import setup
import os


install_requires = [
                    'numpy',
                    #~ 'PyQt5',
                    'pyqtgraph>=0.10.0',
                    'matplotlib>=2.0',
                    'scipy',
                    ]

long_description = ""

#~ import ephyviewer
#~ version = ephyviewer.__version__,
with open('ephyviewer/version.py') as f:
    version = f.readline()[:-1].split('=')[1].replace(' ', '').replace("'", "")


entry_points={'console_scripts': ['ephyviewer=ephyviewer.scripts:launch_standalone_ephyviewer']}


setup(
    name = "ephyviewer",
    version=version,
    packages = ['ephyviewer', 'ephyviewer.datasource', 'ephyviewer.tests'],
    install_requires=install_requires,
    author = "S.Garcia",
    author_email = "sam.garcia.die@gmail.com",
    description = "Simple viewers for ephy stuff",
    entry_points = entry_points,
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
