from setuptools import setup, find_packages
import os


# Read in the README to serve as the long_description, which will be presented
# on pypi.org as the project description.
with open('README.rst', 'r') as f:
    long_description = f.read()

with open('ephyviewer/version.py') as f:
    d = {}
    exec(f.read(), None, d)
    version = d['version']

with open('requirements.txt', 'r') as f:
    install_requires = f.read()

extras_require = {}
with open('requirements-docs.txt', 'r') as f:
    extras_require['docs'] = f.read()
with open('requirements-tests.txt', 'r') as f:
    extras_require['tests'] = f.read()

entry_points={'console_scripts': ['ephyviewer=ephyviewer.scripts:launch_standalone_ephyviewer']}

setup(
    name = 'ephyviewer',
    version = version,
    packages = find_packages(),
    install_requires = install_requires,
    extras_require = extras_require,
    author = 'S.Garcia, Jeffrey Gill',
    author_email = '',  # left blank because multiple emails cannot be provided
    description = 'Simple viewers for ephys signals, events, video and more',
    entry_points = entry_points,
    long_description = long_description,
    license = 'MIT',
    url ='https://github.com/NeuralEnsemble/ephyviewer',
    project_urls = {
        'Documentation': 'https://ephyviewer.readthedocs.io/en/latest/',
        'Source code': 'https://github.com/NeuralEnsemble/ephyviewer/',
        'Bug tracker': 'https://github.com/NeuralEnsemble/ephyviewer/issues',
        'Change log': 'https://ephyviewer.readthedocs.io/en/latest/releasenotes.html',
    },
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        ]
)
