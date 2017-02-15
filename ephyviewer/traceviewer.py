# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

import weakref
import numpy as np


from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer





default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'ylim_max', 'type': 'float', 'value': 10.},
    {'name': 'ylim_min', 'type': 'float', 'value': -10.},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'display_labels', 'type': 'bool', 'value': False},
    ]

default_by_channel_params = [ 
    {'name': 'color', 'type': 'color', 'value': "FF0"},
    {'name': 'gain', 'type': 'float', 'value': 1, 'step': 0.1},
    {'name': 'offset', 'type': 'float', 'value': 0., 'step': 0.1},
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]



class BaseTraceViewerController(QT.QWidget):
    def __init__(self, parent=None, viewer=None):
        QT.QWidget.__init__(self, parent)
        
        # this controller is an attribute of the viewer
        # so weakref to avoid loop reference and Qt crash
        self._viewer = weakref.ref(viewer)
        
        # layout
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        t = 'Options for {}'.format(self.viewer.name)
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QT.QLabel('<b>'+t+'<\b>'))
        

    @property
    def viewer(self):
        return self._viewer()
    
    @property
    def source(self):
        return self._viewer().source




class TraceViewerController(BaseTraceViewerController):
    def __init__(self, parent=None, viewer=None):
        BaseTraceViewerController.__init__(self, parent=parent, viewer=viewer)
        
        

        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.v1 = QT.QVBoxLayout()
        h.addLayout(self.v1)
        self.tree_params = pg.parametertree.ParameterTree()
        self.tree_params.setParameters(self.viewer.params, showTop=True)
        self.tree_params.header().hide()
        self.v1.addWidget(self.tree_params)

        self.tree_by_channel_params = pg.parametertree.ParameterTree()
        self.tree_by_channel_params.header().hide()
        h.addWidget(self.tree_by_channel_params)
        self.tree_by_channel_params.setParameters(self.viewer.by_channel_params, showTop=True)        
        v = QT.QVBoxLayout()
        h.addLayout(v)
        
        
        if self.source.nb_channel>1:
            v.addWidget(QT.QLabel('<b>Select channel...</b>'))
            names = [p.name() for p in self.viewer.by_channel_params]
            self.qlist = QT.QListWidget()
            v.addWidget(self.qlist, 2)
            self.qlist.addItems(names)
            self.qlist.setSelectionMode(QT.QAbstractItemView.ExtendedSelection)
            
            for i in range(len(names)):
                self.qlist.item(i).setSelected(True)            
            v.addWidget(QT.QLabel('<b>and apply...<\b>'))
            
        
        # Gain and offset
        but = QT.QPushButton('set visble')
        v.addWidget(but)
        but.clicked.connect(self.on_set_visible)
        
        for i,text in enumerate(['Real scale (gain = 1, offset = 0)',
                            'Fake scale (same gain for all)',
                            'Fake scale (gain per channel)',]):
            but = QT.QPushButton(text)
            v.addWidget(but)
            but.mode = i
            but.clicked.connect(self.on_auto_gain_and_offset)
        
        
        v.addWidget(QT.QLabel(self.tr('<b>Gain zoom (mouse wheel on graph):</b>'),self))
        h = QT.QHBoxLayout()
        v.addLayout(h)
        for label, factor in [('--', 1./10.), ('-', 1./1.3), ('+', 1.3), ('++', 10.),]:
            but = QT.QPushButton(label)
            but.factor = factor
            but.clicked.connect(self.on_gain_zoom)
            h.addWidget(but)
        
        v.addWidget(QT.QLabel('<b>Set color<\b>'))
        h = QT.QHBoxLayout()
        but = QT.QPushButton('Progressive')
        but.clicked.connect(self.on_automatic_color)
        h.addWidget(but,4)
        self.combo_cmap = QT.QComboBox()
        self.combo_cmap.addItems(['jet', 'prism', 'spring', 'spectral', 'hsv', 'autumn', 'spring', 'summer', 'winter', 'bone'])
        h.addWidget(self.combo_cmap,1)
        v.addLayout(h)
        
    @property
    def selected(self):
        selected = np.ones(self.viewer.nb_channel, dtype=bool)
        if self.viewer.nb_channel>1:
            selected[:] = False
            selected[[ind.row() for ind in self.qlist.selectedIndexes()]] = True
        return selected
    
    def on_set_visible(self):
        # apply
        visibles = self.selected
        for i,param in enumerate(self.viewer.by_channel_params.children()):
            param['visible'] = visibles[i]
    
    def on_auto_gain_and_offset(self):
        mode = self.sender().mode
        self.viewer.auto_gain_and_offset(mode=mode, visibles=self.selected)
    
    def on_gain_zoom(self):
        factor = self.sender().factor
        self.viewer.gain_zoom(factor, selected=self.selected)

    def on_automatic_color(self, cmap_name = None):
        cmap_name = str(self.combo_cmap.currentText())
        if self.source.nb_channel>1:
            selected = self.multi.selected()
        else:
            selected = np.ones(1, dtype = bool)
        self.viewer.automatic_color(cmap_name = cmap_name, selected = selected)



class TraceViewer(BaseMultiChannelViewer):
    _default_params = default_params
    _default_by_channel_params = default_by_channel_params
    
    _ControllerClass = TraceViewerController
    
    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)
        
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF00')
        self.plot.addItem(self.vline)
        
        self._xratio = 0.3
        self._last_chunk = None
    
    
    def refresh(self):
        print('TraceViewer.refresh', 't', self.t)
        
        self.graphicsview.setBackground(self.params['background_color'])
        
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        i_start, i_stop = self.source.time_to_index(t_start), self.source.time_to_index(t_stop)
        
        
        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange(self.params['ylim_min'], self.params['ylim_max'])


        
    
    def estimate_auto_scale(self):
        
        self.factor = 1.
        self.gain_zoom(15.)

    def gain_zoom(self, factor_ratio):
        self.factor *= factor_ratio
        self.gains = np.zeros(self.controller.nb_channel, dtype='float32')
        self.offsets = np.zeros(self.controller.nb_channel, dtype='float32')
        n = np.sum(self.visible_channels)
        self.gains[self.visible_channels] = np.ones(n, dtype=float) * 1./(self.factor*max(self.mad))
        self.offsets[self.visible_channels] = np.arange(n)[::-1] - self.med[self.visible_channels]*self.gains[self.visible_channels]
        self.refresh()
