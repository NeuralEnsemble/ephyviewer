# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

from .myqt import QT




class ViewerBase(QT.QWidget):
    
    time_changed = QT.pyqtSignal()
    
    def __init__(self, *args, **kargs):
        QT.QWidget.__init__(self, *args, **kargs)
        self.t = 0.
    
    def seek(self, t):
        self.t = t
        self.refresh()
    
    def refresh(self):
        #overwrite this one
        raise(NotImplementedError)

