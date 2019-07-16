from setuptools import setup
import os


install_requires = [
                    'numpy',
                    #~ 'PyQt5',
                    'pyqtgraph>=0.10.0',
                    'matplotlib>=2.0',
                    'scipy',
                    ]

# Read in the README to serve as the long_description, which will be presented
# on pypi.org as the project description.
with open('README.md', 'r') as f:
    long_description = f.read()

with open('ephyviewer/version.py') as f:
    d = {}
    exec(f.read(), None, d)
    version = d['version']


entry_points={'console_scripts': ['ephyviewer=ephyviewer.scripts:launch_standalone_ephyviewer']}


setup(
    name = 'ephyviewer',
    version=version,
    packages = ['ephyviewer', 'ephyviewer.datasource', 'ephyviewer.tests', 'ephyviewer.icons'],
    install_requires=install_requires,
    author = 'S.Garcia, Jeffrey Gill',
    author_email = '',  # left blank because multiple emails cannot be provided
    description = 'Simple viewers for ephys signals, events, video and more',
    entry_points = entry_points,
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license = 'MIT',
    url='https://github.com/NeuralEnsemble/ephyviewer',
    project_urls={
        'Documentation': 'https://ephyviewer.readthedocs.io/en/latest/',
        'Source code': 'https://github.com/NeuralEnsemble/ephyviewer/',
        'Bug tracker': 'https://github.com/NeuralEnsemble/ephyviewer/issues',
    },
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        ]
)
