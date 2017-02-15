# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np


class BaseDataSource:
    def __init__(self):
        pass
    
    @property
    def nb_segment(self):
        pass
    
    @property
    def nb_channel(self):
        pass


class BaseAnalogSignalSource(BaseDataSource):
    type = 'AnalogSignal'

    def get_length(self, seg_num=0):
        raise(NotImplementedError)

    def get_shape(self, seg_num=0):
        return (self.get_length(seg_num=seg_num), self.nb_channel)

    def get_chunk(self, seg_num=0, i_start=None, i_stop=None):
        raise(NotImplementedError)


class InMemoryAnalogSignalSource(BaseAnalogSignalSource):
    def __init__(self, signals, sample_rate, t_start):
        BaseAnalogSignalSource.__init__(self)
        
        self.signals = signals
        self.sample_rate = float(sample_rate)
        self.t_start = float(t_start)
    
    @property
    def nb_segment(self):
        return 1

    @property
    def nb_channel(self):
        return self.signals.shape[1]

    def get_length(self, seg_num=0):
        assert seg_num==0
        return self.signals.shape[0]

    def get_chunk(self, seg_num=0, i_start=None, i_stop=None):
        assert seg_num==0
        return self.signals[i_start:i_stop, :]
    
    def time_to_index(self, t):
        return int((t-self.t_start)*self.sample_rate)


    
