# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .sourcebase import BaseDataSource


import matplotlib.cm
import matplotlib.colors


class BaseAnalogSignalSource(BaseDataSource):
    type = 'AnalogSignal'

    def __init__(self):
        self.with_scatter = False
    
    def get_length(self):
        raise(NotImplementedError)

    def get_shape(self):
        return (self.get_length(), self.nb_channel)

    def get_chunk(self, i_start=None, i_stop=None):
        raise(NotImplementedError)

    def time_to_index(self, t):
        return int((t-self.t_start)*self.sample_rate)

    def index_to_time(self, ind):
        return float(ind/self.sample_rate) + self.t_start


class InMemoryAnalogSignalSource(BaseAnalogSignalSource):
    def __init__(self, signals, sample_rate, t_start, channel_names=None):
        BaseAnalogSignalSource.__init__(self)

        self.signals = signals
        self.sample_rate = float(sample_rate)
        self._t_start = float(t_start)
        self._t_stop = self.signals.shape[0]/self.sample_rate + float(t_start)
        self.channel_names = channel_names
        if channel_names is None:
            self.channel_names = ['Channel {:3}'.format(c) for c in range(self.signals.shape[1])]


    @property
    def nb_channel(self):
        return self.signals.shape[1]

    def get_channel_name(self, chan=0):
        return self.channel_names[chan]

    @property
    def t_start(self):
        return self._t_start

    @property
    def t_stop(self):
        return self._t_stop

    def get_length(self):
        return self.signals.shape[0]

    def get_chunk(self, i_start=None, i_stop=None):
        return self.signals[i_start:i_stop, :]




class AnalogSignalSourceWithScatter(InMemoryAnalogSignalSource):
    def __init__(self, signals, sample_rate, t_start, scatter_indexes, scatter_channels, scatter_colors=None, channel_names=None):
        InMemoryAnalogSignalSource.__init__(self, signals, sample_rate, t_start, channel_names=channel_names)
        self.with_scatter = True

        #todo test and assert self.scatter_indexes sorted for eack k
        self.scatter_indexes = scatter_indexes
        self.scatter_channels = scatter_channels
        self.scatter_colors = scatter_colors

        self._labels = list(self.scatter_indexes.keys())

        if self.scatter_colors is None:
            self.scatter_colors = {}
            n = len(self._labels)
            colors = matplotlib.cm.get_cmap('Accent', n)
            for i,k in enumerate(self._labels):
                self.scatter_colors[k] = matplotlib.colors.to_hex(colors(i))

    def get_scatter_babels(self):
        return self._labels

    def get_scatter(self,  i_start=None, i_stop=None, chan=None, label=None):
        if chan not in self.scatter_channels[label]:
            return None

        inds = self.scatter_indexes[label]
        i1 = np.searchsorted(inds, i_start, side='left')
        i2 = np.searchsorted(inds, i_stop, side='left')
        return inds[i1:i2]
