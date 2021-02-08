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
try:
    import PyQt5
    from PyQt5 import QtCore, QtGui, QtWidgets
    QT_MODE = 'PyQt5'
except ImportError:
    try:
        import PySide2
        from PySide2 import QtCore, QtGui, QtWidgets
        QT_MODE = 'PySide2'
    except ImportError:
        try:
            import PyQt4
            from PyQt4 import QtCore, QtGui
            QT_MODE = 'PyQt4'
        except ImportError:
            raise ImportError('Could not locate a supported Qt bindings library (PyQt5, PySide2, PyQt4)')
#~ print(QT_MODE)

if QT_MODE == 'PyQt5':
    QT = ModuleProxy(['', 'Q', 'Qt'], [QtCore.Qt, QtCore, QtGui, QtWidgets])
elif QT_MODE == 'PySide2':
    QT = ModuleProxy(['', 'Q', 'Qt'], [QtCore.Qt, QtCore, QtGui, QtWidgets])
    QT.pyqtSignal = QtCore.Signal  # alias for cross-compatibility with PyQt
elif QT_MODE == 'PyQt4':
    QT = ModuleProxy(['', 'Q', 'Qt'], [QtCore.Qt, QtCore, QtGui])
else:
    QT = None

if QT is not None:
    from pyqtgraph import mkQApp
