# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .sourcebase import BaseDataSource
from .events import BaseEventAndEpoch, InMemoryEventSource


class BaseSpikeSource(BaseEventAndEpoch):
    type = 'Spike'


class InMemorySpikeSource(BaseSpikeSource):

    def __init__(self, all_spikes=[]):
        BaseSpikeSource.__init__(self, all=all_spikes)

        s = [ np.max(e['time']) for e in self.all  if len(e['time'])>0]
        self._t_stop = max(s) if len(s)>0 else 0


    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        spike_times = self.all[chan]['time'][i_start:i_stop]
        return spike_times

    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        spike_times = self.all[chan]['time']

        i1 = np.searchsorted(spike_times, t_start, side='left')
        i2 = np.searchsorted(spike_times, t_stop, side='left')
        sl = slice(i1, i2+1)
        return spike_times[sl]
