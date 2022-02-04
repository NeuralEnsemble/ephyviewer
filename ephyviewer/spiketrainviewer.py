# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController
from .datasource import InMemorySpikeSource, NeoSpikeTrainSource



#make symbol for spikes
from pyqtgraph.graphicsItems.ScatterPlotItem import Symbols
Symbols['|'] = QT.QPainterPath()
Symbols['|'].moveTo(0, -0.5)
Symbols['|'].lineTo(0, 0.5)
Symbols['|'].closeSubpath()




default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'xratio', 'type': 'float', 'value': 0.3, 'step': 0.1, 'limits': (0,1)},
    {'name': 'scatter_size', 'type': 'float', 'value': 0.8,  'limits': (0,np.inf)},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'vline_color', 'type': 'color', 'value': '#FFFFFFAA'},
    {'name': 'label_fill_color', 'type': 'color', 'value': '#222222DD'},
    {'name': 'label_size', 'type': 'int', 'value': 8, 'limits': (1,np.inf)},
    {'name': 'display_labels', 'type': 'bool', 'value': True},
    ]

default_by_channel_params = [
    {'name': 'color', 'type': 'color', 'value': "#55FF00"},
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
        source = InMemorySpikeSource(all_epochs)
        view = cls(source=source, name=name)
        return view

    @classmethod
    def from_neo_spiketrains(cls, neo_spiketrains, name):
        source = NeoSpikeTrainSource(neo_spiketrains)
        view = cls(source=source, name=name)
        return view

    def closeEvent(self, event):
        event.accept()
        self.thread.quit()
        self.thread.wait()


    def initialize_plot(self):
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = self.params['vline_color'])
        self.vline.setZValue(1) # ensure vline is above plot elements
        self.plot.addItem(self.vline)

        self.scatter = pg.ScatterPlotItem(size=self.params['scatter_size'], pxMode = False, symbol='|')
        self.plot.addItem(self.scatter)


        self.labels = []
        for c in range(self.source.nb_channel):
            label_name = '{}: {}'.format(c, self.source.get_channel_name(chan=c))
            color = self.by_channel_params.children()[c].param('color').value()
            label = pg.TextItem(label_name, color=color, anchor=(0, 0.5), border=None, fill=self.params['label_fill_color'])
            font = label.textItem.font()
            font.setPointSize(self.params['label_size'])
            label.setFont(font)
            self.plot.addItem(label)
            self.labels.append(label)

        self.viewBox.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)


    def refresh(self):
        xsize = self.params['xsize']
        xratio = self.params['xratio']
        t_start, t_stop = self.t-xsize*xratio , self.t+xsize*(1-xratio)
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

        for label in self.labels:
            label.fill = pg.mkBrush(self.params['label_fill_color'])

        if len(all_x):
            all_x = np.concatenate(all_x)
            all_y = np.concatenate(all_y)
            all_brush = np.concatenate(all_brush)
            self.scatter.setData(x=all_x, y=all_y, pen=all_brush)

        self.vline.setPen(color=self.params['vline_color'])
        self.vline.setPos(self.t)

        self.plot.setXRange( t_start, t_stop, padding = 0.0)
        self.plot.setYRange(-self.params['scatter_size']/2, self.params['scatter_size']/2 + visibles.size - 1)

    def on_param_change(self, params=None, changes=None):
        for param, change, data in changes:
            if change != 'value': continue
            if param.name()=='scatter_size':
                self.scatter.setSize(self.params['scatter_size'])
            if param.name()=='label_size':
                for label in self.labels:
                    font = label.textItem.font()
                    font.setPointSize(self.params['label_size'])
                    label.setFont(font)

        self.refresh()
