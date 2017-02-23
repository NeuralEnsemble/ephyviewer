# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_ParamController



default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1, 'limits':(0,np.inf)},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'display_labels', 'type': 'bool', 'value': False},
    ]

default_by_channel_params = [ 
    {'name': 'color', 'type': 'color', 'value': "55FF00"},
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]




class EpochViewer_ParamController(Base_ParamController):
    def __init__(self, parent=None, viewer=None):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)


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
            
        
        
        but = QT.QPushButton('set visble')
        v.addWidget(but)
        but.clicked.connect(self.on_set_visible)
    
    @property
    def selected(self):
        selected = np.ones(self.viewer.source.nb_channel, dtype=bool)
        if self.viewer.source.nb_channel>1:
            selected[:] = False
            selected[[ind.row() for ind in self.qlist.selectedIndexes()]] = True
        return selected
    
    @property
    def visible_channels(self):
        visible = [self.viewer.by_channel_params['Channel{}'.format(i), 'visible'] for i in range(self.source.nb_channel)]
        return np.array(visible, dtype='bool')

    def on_set_visible(self):
        # apply
        visibles = self.selected
        for i,param in enumerate(self.viewer.by_channel_params.children()):
            param['visible'] = visibles[i]


class RectItem(pg.GraphicsWidget):
    def __init__(self, rect, border = 'r', fill = 'g'):
        pg.GraphicsWidget.__init__(self)
        self.rect = rect
        self.border= border
        self.fill= fill
    
    def boundingRect(self):
        return QT.QRectF(0, 0, self.rect[2], self.rect[3])
        
    def paint(self, p, *args):
        p.setPen(pg.mkPen(self.border))
        p.setBrush(pg.mkBrush(self.fill))
        p.drawRect(self.boundingRect())


class EpochViewer(BaseMultiChannelViewer):
    _default_params = default_params
    _default_by_channel_params = default_by_channel_params
    
    _ControllerClass = EpochViewer_ParamController
    
    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)
        
        self.initialize_plot()
        
        self._xratio = 0.3
    
    def initialize_plot(self):
        pass
        #~ self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF00')
        #~ self.plot.addItem(self.vline)
        
        #~ self.curves = []
        #~ self.channel_labels = []
        #~ self.channel_offsets_line = []
        #~ for c in range(self.source.nb_channel):
            #~ color = self.by_channel_params['Channel{}'.format(c), 'color']
            #~ curve = pg.PlotCurveItem(pen='#7FFF00')#, connect='finite')
            #~ curve = pg.PlotCurveItem(pen='#7FFF00', downsampleMethod='peak', downsample=1,
                            #~ autoDownsample=False, clipToView=True)#, connect='finite')
            #~ self.plot.addItem(curve)
            #~ self.curves.append(curve)
            
            #~ label = pg.TextItem('chan{}'.format(c), color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 180)))
            #~ self.plot.addItem(label)
            #~ self.channel_labels.append(label)

            #~ offset_line = pg.InfiniteLine(angle = 0, movable = False, pen = '#7FFF00')
            #~ self.plot.addItem(offset_line)
            #~ self.channel_offsets_line.append(offset_line)
        
        #~ self.viewBox.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)
        #~ self.viewBox.ygain_zoom.connect(self.params_controller.apply_ygain_zoom)
    
    
    def refresh(self):
        self.graphicsview.setBackground(self.params['background_color'])
        
        self.plot.clear()
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        
        
        visibles, = np.nonzero(self.params_controller.visible_channels)
        
        
        for e, chan in enumerate(visibles):
            
            times, durations, labels = self.source.get_chunk_by_time(chan=chan,  t_start=t_start, t_stop=t_stop, limit='inside_only')
            #~ self.source.get_chunk_by_time(chan=chan,  t_start=t_start, t_stop=t_stop, limit='outside_also')
            
            for i in range(times.size):
                color = self.by_channel_params.children()[e].param('color').value()
                color2 = QT.QColor(color)
                color2.setAlpha(130)
                item = RectItem([times[i],  visibles.size-e-1,durations[i], .9],  border = color, fill = color2)
                item.setPos(times[i],  visibles.size-e-1)
                self.plot.addItem(item)

        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF00')
        self.plot.addItem(self.vline)

        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( 0, visibles.size)
        self.is_refreshing = False
