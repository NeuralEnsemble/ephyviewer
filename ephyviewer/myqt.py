# -*- coding: utf-8 -*-
"""

Helper for import PyQt5
see
http://mikeboers.com/blog/2015/07/04/static-libraries-in-a-dynamic-world#the-fold
"""

import PyQt5 # this force pyqtgraph to deal with Qt5


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


from PyQt5 import QtCore, QtGui, QtWidgets

QT = ModuleProxy(['', 'Q', 'Qt'], [QtCore.Qt, QtCore, QtGui, QtWidgets])

from pyqtgraph import mkQApp

