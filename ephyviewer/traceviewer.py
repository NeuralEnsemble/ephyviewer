# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_ParamController
from .datasource import InMemoryAnalogSignalSource


#todo remove this
import time
import threading


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1, 'limits':(0,np.inf)},
    {'name': 'ylim_max', 'type': 'float', 'value': 10.},
    {'name': 'ylim_min', 'type': 'float', 'value': -10.},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'display_labels', 'type': 'bool', 'value': False},
    {'name': 'display_offset', 'type': 'bool', 'value': False},
    
    ]

default_by_channel_params = [ 
    {'name': 'color', 'type': 'color', 'value': "55FF00"},
    {'name': 'gain', 'type': 'float', 'value': 1, 'step': 0.1},
    {'name': 'offset', 'type': 'float', 'value': 0., 'step': 0.1},
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]




#TODO use Base_MultiChannel_ParamController instead of Base_ParamController
#to avoid code duplication



class TraceViewer_ParamController(Base_ParamController):
    some_channel_changed = QT.pyqtSignal()
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
            names = [p.name()+': '+p['name'] for p in self.viewer.by_channel_params]
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
        
        h = QT.QHBoxLayout()
        v.addLayout(h)
        h.addWidget(QT.QLabel('Scale mode:'))
        self.combo_scale_mode = QT.QComboBox()
        h.addWidget(self.combo_scale_mode)
        self.scale_modes = ['Real scale',
                            'Spread (same gain for all)',
                            'Spread (gain per channel)',]
        self.combo_scale_mode.addItems(self.scale_modes)
        self.combo_scale_mode.currentIndexChanged.connect(self.on_scale_mode_changed)
        self.scale_mode_index = 0
        #~ for i,text in enumerate():
            #~ but = QT.QPushButton(text)
            #~ v.addWidget(but)
            #~ but.mode = i
            #~ but.clicked.connect(self.on_auto_gain_and_offset)
        
        
        v.addWidget(QT.QLabel(self.tr('<b>Gain zoom (mouse wheel on graph):</b>'),self))
        h = QT.QHBoxLayout()
        v.addLayout(h)
        for label, factor in [('--', 1./5.), ('-', 1./1.1), ('+', 1.1), ('++', 5.),]:
            but = QT.QPushButton(label)
            but.factor = factor
            but.clicked.connect(self.on_but_ygain_zoom)
            h.addWidget(but)
        
        v.addWidget(QT.QLabel('<b>Set color<\b>'))
        h = QT.QHBoxLayout()
        but = QT.QPushButton('Progressive')
        but.clicked.connect(self.on_automatic_color)
        h.addWidget(but,4)
        self.combo_cmap = QT.QComboBox()
        self.combo_cmap.addItems(['Accent', 'Dark2','jet', 'prism', 'hsv', ])
        h.addWidget(self.combo_cmap,1)
        v.addLayout(h)
        
        self.ygain_factor = 1.
        
    @property
    def selected(self):
        selected = np.ones(self.viewer.source.nb_channel, dtype=bool)
        if self.viewer.source.nb_channel>1:
            selected[:] = False
            selected[[ind.row() for ind in self.qlist.selectedIndexes()]] = True
        return selected
    
    @property
    def visible_channels(self):
        visible = [self.viewer.by_channel_params['ch{}'.format(i), 'visible'] for i in range(self.source.nb_channel)]
        return np.array(visible, dtype='bool')

    @property
    def gains(self):
        gains = [self.viewer.by_channel_params['ch{}'.format(i), 'gain'] for i in range(self.source.nb_channel)]
        return np.array(gains)

    @gains.setter
    def gains(self, val):
        for c, v in enumerate(val):
            self.viewer.by_channel_params['ch{}'.format(c), 'gain'] = v

    @property
    def offsets(self):
        offsets = [self.viewer.by_channel_params['ch{}'.format(i), 'offset'] for i in range(self.source.nb_channel)]
        return np.array(offsets)

    @offsets.setter
    def offsets(self, val):
        for c, v in enumerate(val):
            self.viewer.by_channel_params['ch{}'.format(c), 'offset'] = v

    
    def on_set_visible(self):
        # apply
        visibles = self.selected
        for i,param in enumerate(self.viewer.by_channel_params.children()):
            param['visible'] = visibles[i]
    
    def estimate_median_mad(self):
        sigs = self.viewer.last_sigs_chunk
        assert sigs is not None, 'Need to debug this'
        self.signals_med = med = np.median(sigs, axis=0)
        self.signals_mad = np.median(np.abs(sigs-med),axis=0)*1.4826
        #~ print('self.signals_med', self.signals_med)

    
    def on_scale_mode_changed(self, mode_index):
        self.scale_mode_index = mode_index
        self.scale_mode = self.scale_modes[mode_index]
        #~ print('on_scale_mode_changed', mode_index,self.scale_mode)
        
        self.viewer.all_params.sigTreeStateChanged.disconnect(self.viewer.on_param_change)
        
        gains = np.ones(self.viewer.source.nb_channel)
        offsets = np.zeros(self.viewer.source.nb_channel)
        nb_visible = np.sum(self.visible_channels)
        self.ygain_factor = 1
        if self.scale_mode_index==0:
            self.viewer.params['ylim_min'] = np.min(self.viewer.last_sigs_chunk)
            self.viewer.params['ylim_max'] = np.max(self.viewer.last_sigs_chunk)
        else:
            self.estimate_median_mad()
            if self.scale_mode_index==1:
                gains[self.visible_channels] = np.ones(nb_visible, dtype=float) / max(self.signals_mad[self.visible_channels]) / 9.
            elif self.scale_mode_index==2:
                gains[self.visible_channels] = np.ones(nb_visible, dtype=float) / self.signals_mad[self.visible_channels] / 9.
            offsets[self.visible_channels] = np.arange(nb_visible)[::-1] - self.signals_med[self.visible_channels]*gains[self.visible_channels]
            self.viewer.params['ylim_min'] = -0.5
            self.viewer.params['ylim_max'] = nb_visible-0.5
            
        self.gains = gains
        self.offsets = offsets
        self.viewer.all_params.sigTreeStateChanged.connect(self.viewer.on_param_change)
        self.viewer.refresh()
    
    def on_but_ygain_zoom(self):
        factor = self.sender().factor
        self.apply_ygain_zoom(factor)

    def apply_ygain_zoom(self, factor_ratio):
        
        if self.scale_mode_index==0:
            pass
            #TODO ylims
        else :
            self.ygain_factor *= factor_ratio
            self.viewer.all_params.sigTreeStateChanged.disconnect(self.viewer.on_param_change)
            self.gains = self.gains * factor_ratio
            self.offsets = self.offsets + self.signals_med*self.gains * (1-factor_ratio)
            self.viewer.all_params.sigTreeStateChanged.connect(self.viewer.on_param_change)
            self.viewer.refresh()
        print('apply_ygain_zoom', factor_ratio, 'self.ygain_factor', self.ygain_factor)
        
    def apply_xsize_zoom(self, xmove):
        factor = xmove/100.
        newsize = self.viewer.params['xsize']*(factor+1.)
        self.viewer.params['xsize'] = newsize

    def on_automatic_color(self, cmap_name = None):
        cmap_name = str(self.combo_cmap.currentText())
        n = np.sum(self.selected)
        if n==0: return
        cmap = matplotlib.cm.get_cmap(cmap_name , n)
        
        self.viewer.all_params.sigTreeStateChanged.disconnect(self.viewer.on_param_change)
        for i, c in enumerate(np.nonzero(self.selected)[0]):
            color = [ int(e*255) for e in  matplotlib.colors.ColorConverter().to_rgb(cmap(i)) ]
            self.viewer.by_channel_params['ch{}'.format(c), 'color'] = color
        self.viewer.all_params.sigTreeStateChanged.connect(self.viewer.on_param_change)
        self.viewer.refresh()



class DataGrabber(QT.QObject):
    data_ready = QT.pyqtSignal(float, float, float, object, object, object, object)
    
    def __init__(self, source,viewer, parent=None):
        QT.QObject.__init__(self, parent)
        self.source = source
        self.viewer = viewer
        self._max_point = 3000
        
    def on_request_data(self, t, t_start, t_stop, gains, offsets, visibles):
        #~ print('on_request_data', t_start, t_stop)
        
        if self.viewer.t != t:
            #~ print('on_request_data not same t')
            return
        
        i_start, i_stop = self.source.time_to_index(t_start), self.source.time_to_index(t_stop)
        #~ print(t_start, t_stop, i_start, i_stop)
        
        ds_ratio = (i_stop - i_start)//self._max_point + 1
        #~ print()
        #~ print('ds_ratio', ds_ratio)
        
        if ds_ratio>1:
            i_start = i_start - (i_start%ds_ratio)
            i_stop = i_stop - (i_stop%ds_ratio)
            #~ print('i_start, i_stop', i_start, i_stop)
        
        #clip it
        i_start = max(0, i_start)
        i_start = min(i_start, self.source.get_length())
        i_stop = max(0, i_stop)
        i_stop = min(i_stop, self.source.get_length())
        if ds_ratio>1:
            #after clip
            i_start = i_start - (i_start%ds_ratio)
            i_stop = i_stop - (i_stop%ds_ratio)
        
        sigs_chunk = self.source.get_chunk(i_start=i_start, i_stop=i_stop)
        
        
        
        #~ print('sigs_chunk.shape', sigs_chunk.shape)
        data_curves = sigs_chunk[:, visibles].T.copy()
        if data_curves.dtype!='float32':
            data_curves = data_curves.astype('float32')
        
        if ds_ratio>1:
            
            #method decimate pur
            #data_curves = data_curves[:, ::ds_ratio]
            
            #method min_max
            #~ print('data_curves.shape', data_curves.shape)
            small_size = (data_curves.shape[1]//ds_ratio)*2
            #~ print('small_size', small_size)
            small_arr = np.empty((data_curves.shape[0], small_size), dtype=data_curves.dtype)
            #~ full_arr = data_curves[:, :data_curves.shape[1]-data_curves.shape[1]%ds_ratio]
            
            full_arr = data_curves.reshape(data_curves.shape[0], -1, ds_ratio)
            small_arr[:, ::2] = full_arr.max(axis=2)
            small_arr[:, 1::2] = full_arr.min(axis=2)
            data_curves = small_arr
        
        #~ print(data_curves.shape)
        
            
        data_curves *= gains[visibles, None]
        data_curves += offsets[visibles, None]
        dict_curves ={}
        for i, c in enumerate(visibles):
            dict_curves[c] = data_curves[i, :]
            
        times_curves = np.arange(data_curves.shape[1], dtype='float32')
        times_curves /= 2*self.source.sample_rate/ds_ratio
        times_curves += self.source.index_to_time(i_start)
        
        #~ print('on_request_data', threading.get_ident())
        #~ time.sleep(1.)
        self.data_ready.emit(t, t_start, t_stop, visibles, dict_curves, times_curves, sigs_chunk)




class TraceViewer(BaseMultiChannelViewer):
    _default_params = default_params
    _default_by_channel_params = default_by_channel_params
    
    _ControllerClass = TraceViewer_ParamController
    
    request_data = QT.pyqtSignal(float, float, float, object, object, object)
    
    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)

        self.make_params()
        self.set_layout()
        self.make_param_controller()
        
        self.viewBox.doubleclicked.connect(self.show_params_controller)
        
        self.initialize_plot()
        
        self._xratio = 0.3
        
        self.last_sigs_chunk = None

        self.thread = QT.QThread(parent=self)
        self.datagrabber = DataGrabber(source=self.source, viewer=self)
        self.datagrabber.moveToThread(self.thread)
        self.thread.start()
        
        
        self.datagrabber.data_ready.connect(self.on_data_ready)
        self.request_data.connect(self.datagrabber.on_request_data)
    
    @classmethod
    def from_numpy(cls, sigs, sample_rate, t_start, name, channel_names=None):
        source = InMemoryAnalogSignalSource(sigs, sample_rate, t_start, channel_names=channel_names)
        view = cls(source=source, name=name)
        return view

    def closeEvent(self, event):
        event.accept()
        self.thread.quit()
        self.thread.wait()
        
    
    def initialize_plot(self):
        
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF00')
        self.plot.addItem(self.vline)
        
        self.curves = []
        self.channel_labels = []
        self.channel_offsets_line = []
        for c in range(self.source.nb_channel):
            color = self.by_channel_params['ch{}'.format(c), 'color']
            #~ curve = pg.PlotCurveItem(pen='#7FFF00')#, connect='finite')
            curve = pg.PlotCurveItem(pen='#7FFF00', downsampleMethod='peak', downsample=1,
                            autoDownsample=False, clipToView=True)#, connect='finite')
            self.plot.addItem(curve)
            self.curves.append(curve)
            
            ch_name = '{}: {}'.format(c, self.source.get_channel_name(chan=c))
            label = pg.TextItem(ch_name, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 180)))
            
            self.plot.addItem(label)
            self.channel_labels.append(label)

            offset_line = pg.InfiniteLine(angle = 0, movable = False, pen = '#7FFF00')
            self.plot.addItem(offset_line)
            self.channel_offsets_line.append(offset_line)
        
        self.viewBox.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)
        self.viewBox.ygain_zoom.connect(self.params_controller.apply_ygain_zoom)
    
    
    def refresh(self):
        #~ print('TraceViewer.refresh', 't', self.t)
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        visibles, = np.nonzero(self.params_controller.visible_channels)
        gains = self.params_controller.gains
        offsets = self.params_controller.offsets

        self.request_data.emit(self.t, t_start, t_stop, gains, offsets, visibles)
        
        #~ print('refresh', threading.get_ident())


    
    
        


        
        

        #~ self.graphicsview.repaint()
    
    def on_data_ready(self, t,   t_start, t_stop, visibles, dict_curves, times_curves, sigs_chunk):
        #~ print('on_data_ready', t, t_start, t_stop)
        
        if self.t != t:
            #~ print('on_data_ready not same t')
            return
        
        
        self.last_sigs_chunk = sigs_chunk
        offsets = self.params_controller.offsets
        self.graphicsview.setBackground(self.params['background_color'])
    
        
        for i, c in enumerate(visibles):
            self.curves[c].show()
            self.curves[c].setData(times_curves, dict_curves[c])
            
            color = self.by_channel_params['ch{}'.format(c), 'color']
            self.curves[c].setPen(color)
            
            if self.params['display_labels']:
                self.channel_labels[c].show()
                self.channel_labels[c].setPos(t_start, offsets[c])
                self.channel_labels[c].setColor(color)
            else:
                self.channel_labels[c].hide()
            
            if self.params['display_offset']:
                self.channel_offsets_line[c].show()
                self.channel_offsets_line[c].setPos(offsets[c])
                self.channel_offsets_line[c].setPen(color)
            else:
                self.channel_offsets_line[c].hide()
            
        
        #~ index_not_visible, = np.nonzero(~visible_channels)
        for c in range(self.source.nb_channel):
        #~ for i, c in enumerate(index_not_visible):
            if c not in visibles:
                self.curves[c].hide()
                self.channel_labels[c].hide()
                self.channel_offsets_line[c].hide()
        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop, padding = 0.0)
        self.plot.setYRange(self.params['ylim_min'], self.params['ylim_max'], padding = 0.0)

