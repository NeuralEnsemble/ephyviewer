# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .myqt import QT
import pyqtgraph as pg

from .base import ViewerBase
from .datasource import InMemoryEventSource, NeoEventSource




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

        self.combo.addItems([self.source.get_channel_name(i) for i in range(self.source.nb_channel) ])

        self.list_widget.itemClicked.connect(self.select_event)

    @classmethod
    def from_numpy(cls, all_events, name):
        source = InMemoryEventSource(all_events)
        view = cls(source=source, name=name)
        return view

    @classmethod
    def from_neo_events(cls, neo_events, name):
        source = NeoEventSource(neo_events)
        view = cls(source=source, name=name)
        return view

    def refresh(self):
        pass

    def refresh_list(self, ind):
        self.ind = ind
        self.list_widget.clear()
        #~ ev = self.source.all_events[ind]
        data = self.source.get_chunk(chan=ind,  i_start=None, i_stop=None)

        if len(data)==2:
            times, labels = data
        elif len(data)==3:
            times, _, labels = data
        elif len(data)==4:
            times, _, labels, _ = data
        else:
            raise ValueError("data has unexpected dimensions")

        for i in range(times.size):
            if labels is None:
                self.list_widget.addItem('{} : {:.3f}'.format(i, times[i]) )
            else:
                self.list_widget.addItem('{} : {:.3f} {}'.format(i, times[i], labels[i]) )


    def select_event(self):
        i = self.list_widget.currentRow()

        #~ ev = self.source.all_events[self.ind]
        #~ t = ev['time'][i]
        data = self.source.get_chunk(chan=self.ind,  i_start=i, i_stop=i+1)

        if len(data)==2:
            times, labels = data
        elif len(data)==3:
            times, _, labels = data
        elif len(data)==4:
            times, _, labels, _ = data
        else:
            raise ValueError("data has unexpected dimensions")

        if len(times)>0:
            t = float(times[0])
            self.time_changed.emit(t)
