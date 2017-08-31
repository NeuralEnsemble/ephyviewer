# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController
from .datasource import InMemoryEpochSource



#make symbol for spikes
from pyqtgraph.graphicsItems.ScatterPlotItem import Symbols
Symbols['|'] = QT.QPainterPath()
Symbols['|'].moveTo(0, -0.5)
Symbols['|'].lineTo(0, 0.5)
Symbols['|'].closeSubpath()




default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'display_labels', 'type': 'bool', 'value': True},
    ]

default_by_channel_params = [ 
    {'name': 'color', 'type': 'color', 'value': "55FF00"},
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]




class SpikeTrainViewer_ParamController(Base_MultiChannel_ParamController):
    pass



class DataGrabber(QT.QObject):
    data_ready = QT.pyqtSignal(float, float, object, object)
    
    def __init__(self, source, parent=None):
        QT.QObject.__init__(self, parent)
        self.source = source
        
    def on_request_data(self, t_start, t_stop, visibles):
        data = {}
        for e, chan in enumerate(visibles):
            times = self.source.get_chunk_by_time(chan=chan,  t_start=t_start, t_stop=t_stop)
            data[chan] = times
        self.data_ready.emit(t_start, t_stop, visibles, data)
    

class SpikeTrainViewer(BaseMultiChannelViewer):
    _default_params = default_params
    _default_by_channel_params = default_by_channel_params
    
    _ControllerClass = SpikeTrainViewer_ParamController
    
    request_data = QT.pyqtSignal(float, float, object)
    
    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)
        
        self.make_params()
        self.set_layout()
        self.make_param_controller()
        
        self.viewBox.doubleclicked.connect(self.show_params_controller)
        
        self._xratio = 0.3
        
        self.initialize_plot()
        
        
        
        self.thread = QT.QThread(parent=self)
        self.datagrabber = DataGrabber(source=self.source)
        self.datagrabber.moveToThread(self.thread)
        self.thread.start()
        
        
        self.datagrabber.data_ready.connect(self.on_data_ready)
        self.request_data.connect(self.datagrabber.on_request_data)
        
        self.params.param('xsize').setLimits((0, np.inf))

    @classmethod
    def from_numpy(cls, all_epochs, name):
        source = InMemoryEpochSource(all_epochs)
        view = cls(source=source, name=name)
        return view
    
    def closeEvent(self, event):
        event.accept()
        self.thread.quit()
        self.thread.wait()

    
    def initialize_plot(self):
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF00')
        self.plot.addItem(self.vline)
        
        self.scatter = pg.ScatterPlotItem(size=10, pxMode = True, symbol='|')
        self.plot.addItem(self.scatter)
        
        
        self.labels = []
        for c in range(self.source.nb_channel):
            label_name = '{}: {}'.format(c, self.source.get_channel_name(chan=c))
            color = self.by_channel_params.children()[c].param('color').value()
            label = pg.TextItem(label_name, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 180)))
            self.plot.addItem(label)
            self.labels.append(label)
    
    def refresh(self):
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        visibles, = np.nonzero(self.params_controller.visible_channels)
        self.request_data.emit(t_start, t_stop, visibles)

    def on_data_ready(self, t_start, t_stop, visibles, data):
        self.graphicsview.setBackground(self.params['background_color'])
        
        self.scatter.clear()
        all_x = []
        all_y = []
        all_brush = []
        
        for e, chan in enumerate(visibles):
            times = data[chan]

            ypos = visibles.size-e-1
            
            all_x.append(times)
            all_y.append(np.ones(times.size)*ypos)
            color = self.by_channel_params.children()[chan].param('color').value()
            all_brush.append(np.array([pg.mkPen(color)]*len(times)))
            
            
            if self.params['display_labels']:
                self.labels[chan].setPos(t_start, ypos)
                self.labels[chan].show()
                self.labels[chan].setColor(color)

        for chan in range(self.source.nb_channel):
            if not self.params['display_labels'] or chan not in visibles:
                self.labels[chan].hide()

        if len(all_x):
            all_x = np.concatenate(all_x)
            all_y = np.concatenate(all_y)
            all_brush = np.concatenate(all_brush)
            self.scatter.setData(x=all_x, y=all_y, pen=all_brush)

        self.vline.setPos(self.t)
        
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( 0, visibles.size)


