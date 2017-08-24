# -*- coding: utf-8 -*-
"""

Helper for import PyQt5/PtQt4
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
except :
    try:
        import PyQt4
        from PyQt4 import QtCore, QtGui
        QT_MODE = 'PyQt4'
    except ImportError:
        print('no PyQt5/PyQt4')
#~ print(QT_MODE)

if QT_MODE == 'PyQt5':
    #~ from PyQt5 import QtCore, QtGui, QtWidgets
    QT = ModuleProxy(['', 'Q', 'Qt'], [QtCore.Qt, QtCore, QtGui, QtWidgets])
elif QT_MODE == 'PyQt4':
    #~ from PyQt4 import QtCore, QtGui
    QT = ModuleProxy(['', 'Q', 'Qt'], [QtCore.Qt, QtCore, QtGui])
else:
    QT = None

if QT is not None:
    from pyqtgraph import mkQApp



