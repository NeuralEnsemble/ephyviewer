# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController
from .datasource import InMemoryEpochSource


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'display_labels', 'type': 'bool', 'value': True},
    ]

default_by_channel_params = [ 
    {'name': 'color', 'type': 'color', 'value': "55FF00"},
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]




class EpochViewer_ParamController(Base_MultiChannel_ParamController):
    pass




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


class DataGrabber(QT.QObject):
    data_ready = QT.pyqtSignal(float, float, object, object)
    
    def __init__(self, source, parent=None):
        QT.QObject.__init__(self, parent)
        self.source = source
        
    def on_request_data(self, t_start, t_stop, visibles):
        data = {}
        for e, chan in enumerate(visibles):
            times, durations, labels = self.source.get_chunk_by_time(chan=chan,  t_start=t_start, t_stop=t_stop)
            data[chan] = (times, durations, labels)
        self.data_ready.emit(t_start, t_stop, visibles, data)
    

class EpochViewer(BaseMultiChannelViewer):
    _default_params = default_params
    _default_by_channel_params = default_by_channel_params
    
    _ControllerClass = EpochViewer_ParamController
    
    request_data = QT.pyqtSignal(float, float, object)
    
    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)
        
        self.make_params()
        self.set_layout()
        self.make_param_controller()
        
        self.viewBox.doubleclicked.connect(self.show_params_controller)
        
        self.initialize_plot()
        
        self._xratio = 0.3
        
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
        pass
    
    def refresh(self):
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        visibles, = np.nonzero(self.params_controller.visible_channels)
        self.request_data.emit(t_start, t_stop, visibles)

    def on_data_ready(self, t_start, t_stop, visibles, data):
        self.plot.clear()
        self.graphicsview.setBackground(self.params['background_color'])
        
        for e, chan in enumerate(visibles):
            times, durations, labels = data[chan]
            
            color = self.by_channel_params.children()[e].param('color').value()
            color2 = QT.QColor(color)
            color2.setAlpha(130)
            
            ypos = visibles.size-e-1
            
            for i in range(times.size):
                item = RectItem([times[i],  ypos,durations[i], .9],  border = color, fill = color2)
                item.setPos(times[i],  visibles.size-e-1)
                self.plot.addItem(item)

            if self.params['display_labels']:
                label_name = '{}: {}'.format(chan, self.source.get_channel_name(chan=chan))
                label = pg.TextItem(label_name, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 180)))
                self.plot.addItem(label)
                label.setPos(t_start, ypos+0.45)
        
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF0055')
        self.plot.addItem(self.vline)

        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( 0, visibles.size)


