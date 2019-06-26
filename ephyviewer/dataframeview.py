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
        self.qtable.itemClicked.connect(self.on_selection_changed)
        self.mainlayout.addWidget(self.qtable)

        dataframe_on_qtable(self.qtable, self.source)

    def refresh(self):
        pass

    def on_selection_changed(self):
        if 'time' not in self.source.columns:
            return
        ind = [e.row() for e in  self.qtable.selectedIndexes() if e.column()==0]
        if len(ind)==1:
            t = self.source['time'].iloc[ind[0]]
            if t is not None:
                t = float(t)
                if not np.isnan(t):
                    self.time_changed.emit(t)
