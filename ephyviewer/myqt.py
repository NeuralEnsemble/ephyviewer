# -*- coding: utf-8 -*-
"""

Helper for importing Qt bindings library
see
http://mikeboers.com/blog/2015/07/04/static-libraries-in-a-dynamic-world#the-fold
"""


class ModuleProxy(object):

    def __init__(self, prefixes, modules):
        self.prefixes = prefixes
        self.modules = modules

    def __getattr__(self, name):
        for prefix in self.prefixes:
            fullname = prefix + name
            for module in self.modules:
                obj = getattr(module, fullname, None)
                if obj is not None:
                    setattr(self, name, obj) # cache it
                    return obj
        raise AttributeError(name)

QT_MODE = None


if QT_MODE is None:
    try:
        import PySide6
        from PySide6 import QtCore, QtGui, QtWidgets
        QT_MODE = 'PySide6'
    except ImportError:
        pass

#~ if QT_MODE is None:
    #~ try:
        #~ import PyQt6
        #~ from PyQt6 import QtCore, QtGui, QtWidgets
        #~ QT_MODE = 'PyQt6'
    #~ except ImportError:
        #~ pass

if QT_MODE is None:
    try:
        import PyQt5
        from PyQt5 import QtCore, QtGui, QtWidgets
        QT_MODE = 'PyQt5'
    except ImportError:
        pass

if QT_MODE is None:
    try:
        import PySide2
        from PySide2 import QtCore, QtGui, QtWidgets
        QT_MODE = 'PySide2'
    except ImportError:
        pass

if QT_MODE is None:
    try:
        import PyQt4
        from PyQt4 import QtCore, QtGui
        QT_MODE = 'PyQt4'
    except ImportError:
        pass


if QT_MODE is None:
    raise ImportError('Could not locate a supported Qt bindings library (PySide6, PyQt6, PyQt5, PySide2, PyQt4)')
# print(QT_MODE)

if QT_MODE == 'PyQt4':
    modules = [QtCore.Qt, QtCore, QtGui]
else:
    modules = [QtCore.Qt, QtCore, QtGui, QtWidgets]
QT = ModuleProxy(['', 'Q', 'Qt'], modules)

if QT_MODE.startswith('PySide'):
    QT.pyqtSignal = QtCore.Signal  # alias for cross-compatibility with PyQt

from pyqtgraph import mkQApp

