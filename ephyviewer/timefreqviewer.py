# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np
import scipy.fftpack
import scipy.signal

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController, MyViewBox
from .datasource import InMemoryAnalogSignalSource

from .tools import create_plot_grid


#todo remove this
import time
import threading


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'xratio', 'type': 'float', 'value': 0.3, 'step': 0.1, 'limits': (0,1)},
    {'name': 'nb_column', 'type': 'int', 'value': 4},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'vline_color', 'type': 'color', 'value': '#FFFFFFAA'},
    {'name': 'colormap', 'type': 'list', 'value': 'viridis', 'values' : ['viridis', 'jet', 'gray', 'hot', ] },
    {'name': 'display_labels', 'type': 'bool', 'value': True},
    {'name': 'show_axis', 'type': 'bool', 'value': True},
    {'name': 'scale_mode', 'type': 'list', 'value': 'same_for_all', 'values' : ['by_channel', 'same_for_all', ] },
    {'name': 'timefreq', 'type': 'group', 'children': [
                    {'name': 'f_start', 'type': 'float', 'value': 3., 'step': 1.},
                    {'name': 'f_stop', 'type': 'float', 'value': 90., 'step': 1.},
                    {'name': 'deltafreq', 'type': 'float', 'value': 3., 'step': 1., 'limits': [0.1, 1.e6]},
                    {'name': 'f0', 'type': 'float', 'value': 2.5, 'step': 0.1},
                    {'name': 'normalisation', 'type': 'float', 'value': 0., 'step': 0.1},]}

    ]

default_by_channel_params = [
    {'name': 'visible', 'type': 'bool', 'value': True},
    {'name': 'clim', 'type': 'float', 'value': .1},
    ]


def generate_wavelet_fourier(len_wavelet, f_start, f_stop, deltafreq, sample_rate, f0, normalisation):
    """
    Compute the wavelet coefficients at all scales and compute its Fourier transform.

    Parameters
    ----------
    len_wavelet : int
        length in samples of the wavelet window
    f_start: float
        First frequency in Hz
    f_stop: float
        Last frequency in Hz
    deltafreq : float
        Frequency interval in Hz
    sample_rate : float
        Sample rate in Hz
    f0 : float
    normalisation : float

    Returns:
    -------

    wf : array
        Fourier transform of the wavelet coefficients (after weighting).
        Axis 0 is time; axis 1 is frequency.
    """
    # compute final map scales
    scales = f0/np.arange(f_start,f_stop,deltafreq)*sample_rate

    # compute wavelet coeffs at all scales
    xi=np.arange(-len_wavelet/2.,len_wavelet/2.)
    xsd = xi[:,np.newaxis] / scales
    wavelet_coefs=np.exp(complex(1j)*2.*np.pi*f0*xsd)*np.exp(-np.power(xsd,2)/2.)

    weighting_function = lambda x: x**(-(1.0+normalisation))
    wavelet_coefs = wavelet_coefs*weighting_function(scales[np.newaxis,:])

    # Transform the wavelet into the Fourier domain
    wf=scipy.fftpack.fft(wavelet_coefs,axis=0)
    wf=wf.conj()

    return wf



class TimeFreqViewer_ParamController(Base_MultiChannel_ParamController):
    some_clim_changed = QT.pyqtSignal()

    def on_channel_visibility_changed(self):
        print('TimeFreqViewer_ParamController.on_channel_visibility_changed')
        self.viewer.create_grid()
        self.viewer.initialize_time_freq()
        self.viewer.refresh()

    def clim_zoom(self, factor):
        #~ print('clim_zoom factor', factor)
        self.viewer.by_channel_params.blockSignals(True)

        for i, p in enumerate(self.viewer.by_channel_params.children()):
            p.param('clim').setValue(p.param('clim').value()*factor)

        self.viewer.by_channel_params.blockSignals(False)
        self.some_clim_changed.emit()

    def compute_auto_clim(self):
        print('compute_auto_clim')
        print(self.visible_channels)

        self.viewer.by_channel_params.blockSignals(True)
        maxs = []
        visibles,  = np.nonzero(self.visible_channels)
        for chan in visibles:
            if chan in self.viewer.last_wt_maps.keys():
                m = np.max(self.viewer.last_wt_maps[chan])
                if self.viewer.params['scale_mode'] == 'by_channel':
                    self.viewer.by_channel_params['ch'+str(chan), 'clim'] = m
                else:
                    maxs.append(m)
        if self.viewer.params['scale_mode'] == 'same_for_all' and len(maxs)>0:
            for chan in visibles:
                self.viewer.by_channel_params['ch'+str(chan), 'clim'] = max(maxs)

        self.viewer.by_channel_params.blockSignals(False)
        self.some_clim_changed.emit()


class TimeFreqWorker(QT.QObject):
    data_ready = QT.pyqtSignal(int, float, float, float,  float, float, object)

    def __init__(self, source,viewer, chan,  parent=None):
        QT.QObject.__init__(self, parent)
        self.source = source
        self.viewer = viewer
        self.chan = chan

    def on_request_data(self, chan, t, t_start, t_stop, visible_channels, worker_params):
        if chan != self.chan:
            return

        if not visible_channels[chan]:
            return

        if self.viewer.t != t:
            print('viewer has moved already', chan, self.viewer.t, t)
            # viewer has moved already
            return

        ds_ratio = worker_params['downsample_ratio']
        sig_chunk_size = worker_params['sig_chunk_size']
        filter_sos = worker_params['filter_sos']
        wavelet_fourrier = worker_params['wavelet_fourrier']
        plot_length = worker_params['plot_length']

        i_start = self.source.time_to_index(t_start)
        #~ print('ds_ratio', ds_ratio)
        #~ print('start', t_start, i_start)

        if ds_ratio>1:
            i_start = i_start - (i_start%ds_ratio)
            #~ print('start', t_start, i_start)

        #clip it
        i_start = max(0, i_start)
        i_start = min(i_start, self.source.get_length())
        if ds_ratio>1:
            #after clip
            i_start = i_start - (i_start%ds_ratio)
        #~ print('start', t_start, i_start)

        i_stop = i_start + sig_chunk_size
        i_stop = min(i_stop, self.source.get_length())


        sigs_chunk = self.source.get_chunk(i_start=i_start, i_stop=i_stop)
        sig = sigs_chunk[:, chan]

        if ds_ratio>1:
            small_sig = scipy.signal.sosfiltfilt(filter_sos, sig)
            small_sig =small_sig[::ds_ratio].copy()  # to ensure continuity
        else:
            small_sig = sig.copy()# to ensure continuity

        left_pad = 0
        if small_sig.shape[0] != wavelet_fourrier.shape[0]:
            #Pad it
            z = np.zeros(wavelet_fourrier.shape[0], dtype=small_sig.dtype)
            left_pad = wavelet_fourrier.shape[0] - small_sig.shape[0]
            z[:small_sig.shape[0]] = small_sig
            small_sig = z


        #avoid border effect
        small_sig -= small_sig.mean()

        #~ print('sig', sig.shape, 'small_sig', small_sig.shape)

        small_sig_f = scipy.fftpack.fft(small_sig)
        if small_sig_f.shape[0] != wavelet_fourrier.shape[0]:
            print('oulala', small_sig_f.shape, wavelet_fourrier.shape)
            #TODO pad with zeros somewhere
            return
        wt_tmp=scipy.fftpack.ifft(small_sig_f[:,np.newaxis]*wavelet_fourrier,axis=0)
        wt = scipy.fftpack.fftshift(wt_tmp,axes=[0])
        wt = np.abs(wt).astype('float32')
        if left_pad>0:
            wt = wt[:-left_pad]
        wt_map = wt[:plot_length]
        #~ wt_map =wt
        #~ print('wt_map', wt_map.shape)


        #~ print('sleep', chan)
        #~ time.sleep(2.)

        #TODO t_start and t_stop wrong
        #~ print('sub_sample_rate', worker_params['sub_sample_rate'])
        #~ print('wanted_size', worker_params['wanted_size'])
        #~ print('plot_length', plot_length)
        #~ print(i_start, i_stop)
        t1 = self.source.index_to_time(i_start)
        t2 = self.source.index_to_time(i_start+wt_map.shape[0]*ds_ratio)
        #~ t2 = self.source.index_to_time(i_stop)
        self.data_ready.emit(chan, t,   t_start, t_stop, t1, t2, wt_map)


class TimeFreqViewer(BaseMultiChannelViewer):

    _default_params = default_params
    _default_by_channel_params = default_by_channel_params

    _ControllerClass = TimeFreqViewer_ParamController

    request_data = QT.pyqtSignal(int, float, float, float, object, object)

    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)

        self.make_params()

        # make all not visible
        self.by_channel_params.blockSignals(True)
        for c in range(self.source.nb_channel):
            self.by_channel_params['ch'+str(c), 'visible'] = c==0
        self.by_channel_params.blockSignals(False)

        self.make_param_controller()
        self.params_controller.some_clim_changed.connect(self.refresh)

        self.set_layout()

        self.change_color_scale()
        self.create_grid()
        self.initialize_time_freq()


        self.last_wt_maps = {}

        self.threads = []
        self.timefreq_makers = []
        for c in range(self.source.nb_channel):
            thread = QT.QThread(parent=self)
            self.threads.append(thread)
            worker = TimeFreqWorker(self.source, self, c)
            self.timefreq_makers.append(worker)
            worker.moveToThread(thread)
            thread.start()


            worker.data_ready.connect(self.on_data_ready)
            self.request_data.connect(worker.on_request_data)

        self.params.param('xsize').setLimits((0, np.inf))

    @classmethod
    def from_numpy(cls, sigs, sample_rate, t_start, name, channel_names=None):
        source = InMemoryAnalogSignalSource(sigs, sample_rate, t_start, channel_names=channel_names)
        view = cls(source=source, name=name)
        return view

    def closeEvent(self, event):
        for i, thread in enumerate(self.threads):
            thread.quit()
            thread.wait()
        event.accept()

    def set_layout(self):
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.graphiclayout = pg.GraphicsLayoutWidget()
        self.mainlayout.addWidget(self.graphiclayout)

    def on_param_change(self, params=None, changes=None):
        #~ print('on_param_change')
        #track if new scale mode
        #~ for param, change, data in changes:
            #~ if change != 'value': continue
            #~ if param.name()=='scale_mode':
                #~ self.params_controller.compute_rescale()

        #for simplification everything is recompute
        self.change_color_scale()
        self.create_grid()
        self.initialize_time_freq()
        self.refresh()

    def create_grid(self):
        visible_channels = self.params_controller.visible_channels

        self.plots = create_plot_grid(self.graphiclayout, self.params['nb_column'], visible_channels,
                         ViewBoxClass=MyViewBox,  vb_params={})

        for plot in self.plots:
            if plot is not None:
                plot.vb.doubleclicked.connect(self.show_params_controller)
                plot.vb.ygain_zoom.connect(self.params_controller.clim_zoom)
                # plot.vb.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)

        self.images = []
        self.vlines = []
        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                image = pg.ImageItem()
                self.plots[c].addItem(image)
                self.images.append(image)

                vline = pg.InfiniteLine(angle = 90, movable = False, pen = self.params['vline_color'])
                vline.setZValue(1) # ensure vline is above plot elements
                self.plots[c].addItem(vline)
                self.vlines.append(vline)

            else:
                self.images.append(None)
                self.vlines.append(None)

    def initialize_time_freq(self):
        tfr_params = self.params.param('timefreq')
        sample_rate = self.source.sample_rate

        # we take sample_rate = f_stop*4 or (original sample_rate)
        if tfr_params['f_stop']*4 < sample_rate:
            wanted_sub_sample_rate = tfr_params['f_stop']*4
        else:
            wanted_sub_sample_rate = sample_rate

        # this try to find the best size to get a timefreq of 2**N by changing
        # the sub_sample_rate and the sig_chunk_size
        d = self.worker_params = {}
        d['wanted_size'] = self.params['xsize']
        l = d['len_wavelet'] = int(2**np.ceil(np.log(d['wanted_size']*wanted_sub_sample_rate)/np.log(2)))
        d['sig_chunk_size'] = d['wanted_size']*self.source.sample_rate
        d['downsample_ratio'] = int(np.ceil(d['sig_chunk_size']/l))
        d['sig_chunk_size'] = d['downsample_ratio']*l
        d['sub_sample_rate'] = self.source.sample_rate/d['downsample_ratio']
        d['plot_length'] = int(d['wanted_size']*d['sub_sample_rate'])

        d['wavelet_fourrier'] = generate_wavelet_fourier(d['len_wavelet'], tfr_params['f_start'], tfr_params['f_stop'],
                            tfr_params['deltafreq'], d['sub_sample_rate'], tfr_params['f0'], tfr_params['normalisation'])

        if d['downsample_ratio']>1:
            n = 8
            q = d['downsample_ratio']
            d['filter_sos'] = scipy.signal.cheby1(n, 0.05, 0.8 / q, output='sos')
        else:
            d['filter_sos'] = None

    def change_color_scale(self):
        N = 512
        cmap_name = self.params['colormap']
        cmap = matplotlib.cm.get_cmap(cmap_name , N)

        lut = []
        for i in range(N):
            r,g,b,_ =  matplotlib.colors.ColorConverter().to_rgba(cmap(i))
            lut.append([r*255,g*255,b*255])
        self.lut = np.array(lut, dtype='uint8')

    def auto_scale(self):
        print('auto_scale', self.params['scale_mode'])
        self.params_controller.compute_auto_clim()
        self.refresh()

    def refresh(self):
        #~ print('TimeFreqViewer.refresh', self.t)
        visible_channels = self.params_controller.visible_channels

        xsize = self.params['xsize']
        xratio = self.params['xratio']
        t_start, t_stop = self.t-xsize*xratio , self.t+xsize*(1-xratio)

        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                self.request_data.emit(c, self.t, t_start, t_stop, visible_channels, self.worker_params)

        self.graphiclayout.setBackground(self.params['background_color'])

    def on_data_ready(self, chan, t,   t_start, t_stop, t1,t2, wt_map):
        if not self.params_controller.visible_channels[chan]:
            return

        if self.images[chan] is None:
            return

        self.last_wt_maps[chan] = wt_map
        f_start = self.params['timefreq', 'f_start']
        f_stop = self.params['timefreq', 'f_stop']

        image = self.images[chan]
        #~ print(t_start, f_start,self.worker_params['wanted_size'], f_stop-f_start)

        #~ image.updateImage(wt_map)
        clim = self.by_channel_params['ch{}'.format(chan), 'clim']
        image.setImage(wt_map, lut=self.lut, levels=[0, clim])
        image.setRect(QT.QRectF(t1, f_start,t2-t1, f_stop-f_start))

        #TODO
        # display_labels

        self.vlines[chan].setPos(t)
        self.vlines[chan].setPen(color=self.params['vline_color'])
        plot = self.plots[chan]
        plot.setXRange(t_start, t_stop, padding = 0.0)
        plot.setYRange(f_start, f_stop, padding = 0.0)

        if self.params['display_labels']:
            ch_name = '{}: {}'.format(chan, self.source.get_channel_name(chan=chan))
            self.plots[chan].setTitle(ch_name)
        else:
            self.plots[chan].setTitle(None)


        self.plots[chan].showAxis('left', self.params['show_axis'])
        self.plots[chan].showAxis('bottom', self.params['show_axis'])
