# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .myqt import QT
import pyqtgraph as pg

from .base import ViewerBase





class EventList(ViewerBase):
    
    def __init__(self,  **kargs):
        ViewerBase.__init__(self, **kargs)
        
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        
        self.combo = QT.QComboBox()
        self.mainlayout.addWidget(self.combo)
        self.list_widget = QT.QListWidget()
        self.mainlayout.addWidget(self.list_widget)
        self.combo.currentIndexChanged.connect(self.refresh_list)
        
        self.combo.addItems([ev['name'] for ev in self.source.all_events ])
        
        self.list_widget.currentRowChanged.connect(self.select_event)
        
    def refresh(self):
        pass
        
    def refresh_list(self, ind):
        self.ind = ind
        self.list_widget.clear()
        ev = self.source.all_events[ind]
        for i in range(ev['time'].size):
            if ev['label'] is None:
                self.list_widget.addItem('{} : {:.3f}'.format(i, ev['time'][i]) )
            else:
                self.list_widget.addItem('{} : {:.3f} {}'.format(i, ev['time'][i], ev['label'][i]) )

        
    def select_event(self, i):
        ev = self.source.all_events[self.ind]
        t = ev['time'][i]
        self.time_changed.emit(t)
        