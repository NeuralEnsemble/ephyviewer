# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .myqt import QT
import pyqtgraph as pg

from .base import ViewerBase
from .datasource import InMemoryEventSource


def dataframe_on_qtable(qtable, df):
        qtable.clear()
        qtable.setColumnCount(len(df.columns))
        qtable.setRowCount(len(df.index))
        
        qtable.setHorizontalHeaderLabels(['{}'.format(c) for c in df.columns])
        qtable.setVerticalHeaderLabels(['{}'.format(c) for c in df.index])
        
        for r, row in enumerate(df.index):
            for c, col in enumerate(df.columns):
                try:
                    v = u'{}'.format(df.loc[row,col])
                    qtable.setItem(r, c,  QT.QTableWidgetItem(v))
                except Exception as e:
                    print('erreur', e)
                    print(r, row)
                    print(c, col)



class DataFrameView(ViewerBase):
    
    def __init__(self,  **kargs):
        ViewerBase.__init__(self, **kargs)
        
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        
        self.qtable = QT.QTableWidget(selectionMode=QT.QAbstractItemView.SingleSelection,
                                                                            selectionBehavior=QT.QAbstractItemView.SelectRows)
        self.qtable.itemSelectionChanged.connect(self.on_selection_changed)
        self.mainlayout.addWidget(self.qtable)
        
        dataframe_on_qtable(self.qtable, self.source)
        
    def refresh(self):
        pass
        
    #~ def refresh_list(self, ind):
        #~ self.ind = ind
        #~ self.list_widget.clear()
        #~ ev = self.source.all_events[ind]
        #~ times, labels = self.source.get_chunk(chan=ind,  i_start=None, i_stop=None)
        #~ for i in range(times.size):
            #~ if labels is None:
                #~ self.list_widget.addItem('{} : {:.3f}'.format(i, times[i]) )
            #~ else:
                #~ self.list_widget.addItem('{} : {:.3f} {}'.format(i, times[i], labels[i]) )

    
    def on_selection_changed(self):
        if 'time' not in self.source.columns:
            return
        ind = [e.row() for e in  self.qtable.selectedIndexes() if e.column()==0]
        if len(ind)==1:
            t = float(self.source['time'].iloc[ind[0]])
            self.time_changed.emit(t)
            
        #~ print(ind)

        #~ pass
    
    #~ def select_event(self, i):
        
        #~ ev = self.source.all_events[self.ind]
        #~ t = ev['time'][i]
        #~ times, labels = self.source.get_chunk(chan=self.ind,  i_start=i, i_stop=i+1)
        #~ if len(times)>0:
            #~ t = float(times[0])
            #~ self.time_changed.emit(t)
        