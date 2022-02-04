# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController
from .datasource import InMemoryEpochSource, NeoEpochSource


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'xratio', 'type': 'float', 'value': 0.3, 'step': 0.1, 'limits': (0,1)},
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




class EpochViewer_ParamController(Base_MultiChannel_ParamController):
    pass




class RectItem(pg.GraphicsWidget):

    clicked = QT.pyqtSignal(int)
    doubleclicked = QT.pyqtSignal(int)

    def __init__(self, rect, border = 'r', fill = 'g', id = -1):
        pg.GraphicsWidget.__init__(self)
        self.rect = rect
        self.border= border
        self.fill= fill
        self.id = id

    def boundingRect(self):
        return QT.QRectF(0, 0, self.rect[2], self.rect[3])

    def paint(self, p, *args):
        p.setPen(pg.mkPen(self.border))
        p.setBrush(pg.mkBrush(self.fill))
        p.drawRect(self.boundingRect())

    def mouseClickEvent(self, event):
        if event.button()== QT.LeftButton:
            event.accept()
            if event.double():
                self.doubleclicked.emit(self.id)
            else:
                self.clicked.emit(self.id)
        else:
            event.ignore()


class DataGrabber(QT.QObject):
    data_ready = QT.pyqtSignal(float, float, object, object)

    def __init__(self, source, parent=None):
        QT.QObject.__init__(self, parent)
        self.source = source

    def on_request_data(self, t_start, t_stop, visibles):
        data = {}
        for e, chan in enumerate(visibles):
            data[chan] = self.source.get_chunk_by_time(chan=chan,  t_start=t_start, t_stop=t_stop)
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

    @classmethod
    def from_neo_epochs(cls, neo_epochs, name):
        source = NeoEpochSource(neo_epochs)
        view = cls(source=source, name=name)
        return view

    def closeEvent(self, event):
        event.accept()
        self.thread.quit()
        self.thread.wait()


    def initialize_plot(self):
        self.viewBox.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)

    def refresh(self):
        xsize = self.params['xsize']
        xratio = self.params['xratio']
        t_start, t_stop = self.t-xsize*xratio , self.t+xsize*(1-xratio)
        visibles, = np.nonzero(self.params_controller.visible_channels)
        self.request_data.emit(t_start, t_stop, visibles)

    def on_data_ready(self, t_start, t_stop, visibles, data):
        self.plot.clear()
        self.graphicsview.setBackground(self.params['background_color'])

        for e, chan in enumerate(visibles):

            if len(data[chan])==3:
                times, durations, labels = data[chan]
            elif len(data[chan])==4:
                times, durations, labels, _ = data[chan]
            else:
                raise ValueError("data has unexpected dimensions")

            color = self.by_channel_params.children()[chan].param('color').value()
            color2 = QT.QColor(color)
            color2.setAlpha(130)

            ypos = visibles.size-e-1

            for i in range(times.size):
                item = RectItem([times[i],  ypos,durations[i], .9],  border = color, fill = color2)
                item.setPos(times[i],  visibles.size-e-1)
                self.plot.addItem(item)

            if self.params['display_labels']:
                label_name = '{}: {}'.format(chan, self.source.get_channel_name(chan=chan))
                label = pg.TextItem(label_name, color=color, anchor=(0, 0.5), border=None, fill=self.params['label_fill_color'])
                font = label.textItem.font()
                font.setPointSize(self.params['label_size'])
                label.setFont(font)
                self.plot.addItem(label)
                label.setPos(t_start, ypos+0.45)

        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = self.params['vline_color'])
        self.vline.setZValue(1) # ensure vline is above plot elements
        self.plot.addItem(self.vline)

        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop, padding = 0.0)
        self.plot.setYRange( 0, visibles.size)
