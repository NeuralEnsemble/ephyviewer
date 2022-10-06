import numpy as np
import scipy.fftpack
import scipy.signal

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import BaseMultiChannelViewer, Base_MultiChannel_ParamController, MyViewBox
from .datasource import InMemoryAnalogSignalSource

from .tools import create_plot_grid, get_dict_from_group_param


#todo remove this
import time
import threading



default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 10., 'step': 0.1},
    {'name': 'xratio', 'type': 'float', 'value': 0.3, 'step': 0.1, 'limits': (0,1)},
    {'name': 'nb_column', 'type': 'int', 'value': 4},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'vline_color', 'type': 'color', 'value': '#FFFFFFAA'},
    {'name': 'colormap', 'type': 'list', 'value': 'viridis', 'limits' : ['inferno', 'viridis', 'jet', 'gray', 'hot', ] },
    {'name': 'scale_mode', 'type': 'list', 'value': 'same_for_all', 'limits' : ['by_channel', 'same_for_all', ] },
    {'name': 'display_labels', 'type': 'bool', 'value': True},
    {'name': 'show_axis', 'type': 'bool', 'value': True},
    {'name': 'scalogram', 'type': 'group', 'children': [
                    {'name': 'binsize', 'type': 'float', 'value': 0.01, 'step': .01, 'limits': (0,np.inf)},
                    {'name': 'overlapratio', 'type': 'float', 'value': 0., 'step': .05, 'limits': (0., 0.95)},
                    {'name': 'scaling', 'type': 'list', 'value': 'density', 'limits' : ['density', 'spectrum'] },
                    {'name': 'mode', 'type': 'list', 'value': 'psd', 'limits' : ['psd'] },
                    {'name': 'detrend', 'type': 'list', 'value': 'constant', 'limits' : ['constant'] },
                    {'name': 'scale', 'type': 'list', 'value': 'dB', 'limits' : ['dB', 'linear'] },
                    

                ]
            }
                    
    ]

default_by_channel_params = [
    {'name': 'visible', 'type': 'bool', 'value': True},
    {'name': 'clim_min', 'type': 'float', 'value': -10},
    {'name': 'clim_max', 'type': 'float', 'value': 0.},
    ]
    
    
    
class SpectrogramViewer_ParamController(Base_MultiChannel_ParamController):
    some_clim_changed = QT.pyqtSignal()

    def on_channel_visibility_changed(self):
        #~ print('SpectrogramViewer_ParamController.on_channel_visibility_changed')
        self.viewer.create_grid()
        self.viewer.refresh()

    def clim_zoom(self, factor):
        print('clim_zoom factor', factor)
        self.viewer.by_channel_params.blockSignals(True)

        for i, p in enumerate(self.viewer.by_channel_params.children()):
            # p.param('clim').setValue(p.param('clim').value()*factor)
            min_ = p['clim_min']
            max_ = p['clim_max']
            d = max_ - min_
            m = (min_ + max_) / 2.
            p['clim_min'] = m - d/2. * factor
            p['clim_max'] = m + d/2. * factor

        self.viewer.by_channel_params.blockSignals(False)
        self.some_clim_changed.emit()

    def compute_auto_clim(self):
        #~ print('compute_auto_clim')
        #~ print(self.visible_channels)

        self.viewer.by_channel_params.blockSignals(True)
        mins = []
        maxs = []
        visibles,  = np.nonzero(self.visible_channels)
        for chan in visibles:
            if chan in self.viewer.last_Sxx.keys():
                min_ = np.min(self.viewer.last_Sxx[chan])
                max_ = np.max(self.viewer.last_Sxx[chan])
                if self.viewer.params['scale_mode'] == 'by_channel':
                    self.viewer.by_channel_params['ch'+str(chan), 'clim_min'] = min_
                    self.viewer.by_channel_params['ch'+str(chan), 'clim_max'] = max_
                    
                else:
                    mins.append(min_)
                    maxs.append(max_)
                    
        if self.viewer.params['scale_mode'] == 'same_for_all' and len(maxs)>0:
            for chan in visibles:
                self.viewer.by_channel_params['ch'+str(chan), 'clim_min'] = np.min(mins)
                self.viewer.by_channel_params['ch'+str(chan), 'clim_max'] = np.max(maxs)

        self.viewer.by_channel_params.blockSignals(False)
        self.some_clim_changed.emit()



class SpectrogramWorker(QT.QObject):
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

        binsize = worker_params['binsize']
        overlapratio = worker_params['overlapratio']
        scaling = worker_params['scaling']
        detrend = worker_params['detrend']
        mode = worker_params['mode']
        

        i_start = self.source.time_to_index(t_start)
        i_stop = self.source.time_to_index(t_stop)
        # clip
        i_start = min(max(0, i_start), self.source.get_length())
        i_stop = min(max(0, i_stop), self.source.get_length())
        

        sr = self.source.sample_rate
        nperseg = int(binsize * sr)
        noverlap = int(overlapratio * nperseg)
        
        if noverlap >= nperseg:
            noverlap = noverlap - 1
        print(nperseg, noverlap)

        if nperseg== 0 or (i_stop - i_start) < nperseg:
            # too short
            t1, t2 = t_start, t_stop
            Sxx = None
            self.data_ready.emit(chan, t,   t_start, t_stop, t1, t2, Sxx)
        else:

            sigs_chunk = self.source.get_chunk(i_start=i_start, i_stop=i_stop)
            sig = sigs_chunk[:, chan]

            freqs, times, Sxx = scipy.signal.spectrogram(sig, fs=sr,nperseg=nperseg, noverlap=noverlap,
                        detrend=detrend, scaling=scaling, mode=mode)
            
            if  worker_params['scale'] == 'dB':
                if mode == 'psd':
                    Sxx = 10. * np.log10(Sxx)
            
            if len(times) >=2:
                bin_slide = times[1] - times[0]
                t1 = self.source.index_to_time(i_start) + times[0] - bin_slide /2.
                t2 = self.source.index_to_time(i_start) + times[-1] + bin_slide /2.
                self.data_ready.emit(chan, t,   t_start, t_stop, t1, t2, Sxx)
            else:
                t1, t2 = t_start, t_stop
                Sxx = None
                self.data_ready.emit(chan, t,   t_start, t_stop, t1, t2, Sxx)





class SpectrogramViewer(BaseMultiChannelViewer):

    _default_params = default_params
    _default_by_channel_params = default_by_channel_params

    _ControllerClass = SpectrogramViewer_ParamController

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


        self.last_Sxx = {}

        self.threads = []
        self.timefreq_makers = []
        for c in range(self.source.nb_channel):
            thread = QT.QThread(parent=self)
            self.threads.append(thread)
            worker = SpectrogramWorker(self.source, self, c)
            self.timefreq_makers.append(worker)
            worker.moveToThread(thread)
            thread.start()
            
            self.last_Sxx[c] = None


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
        #~ print('auto_scale', self.params['scale_mode'])
        self.params_controller.compute_auto_clim()
        self.refresh()

    def refresh(self):
        #~ print('TimeFreqViewer.refresh', self.t)
        visible_channels = self.params_controller.visible_channels

        xsize = self.params['xsize']
        xratio = self.params['xratio']
        t_start, t_stop = self.t-xsize*xratio , self.t+xsize*(1-xratio)
        
        worker_params = get_dict_from_group_param(self.params.param('scalogram'))
        #~ print('worker_params', worker_params)
        
        
        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                self.request_data.emit(c, self.t, t_start, t_stop, visible_channels, worker_params)

        self.graphiclayout.setBackground(self.params['background_color'])

    def on_data_ready(self, chan, t,   t_start, t_stop, t1,t2, Sxx):
        if not self.params_controller.visible_channels[chan]:
            return

        if self.images[chan] is None:
            return
        
        
        self.last_Sxx[chan] = Sxx
        
        image = self.images[chan]
        
        if Sxx is None:
            image.hide()
            return
        
        image.show()
        
        f_start = 0
        f_stop = self.source.sample_rate / 2.
        #~ f_start = self.params['timefreq', 'f_start']
        #~ f_stop = self.params['timefreq', 'f_stop']

        
        #~ print(t_start, f_start,self.worker_params['wanted_size'], f_stop-f_start)

        #~ image.updateImage(wt_map)
        clim_min = self.by_channel_params['ch{}'.format(chan), 'clim_min']
        clim_max = self.by_channel_params['ch{}'.format(chan), 'clim_max']
        
        #~ clim = np.max(Sxx)
        image.setImage(Sxx.T, lut=self.lut, levels=[clim_min, clim_max])
        #~ image.setImage(Sxx.T, lut=self.lut, levels=[ np.min(Sxx), np.max(Sxx)])
        image.setRect(QT.QRectF(t1, f_start,t2-t1, f_stop-f_start))

        #TODO
        # display_labels

        self.vlines[chan].setPos(t)
        self.vlines[chan].setPen(self.params['vline_color'])
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



