# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .sourcebase import BaseDataSource



class BaseEventAndEpoch(BaseDataSource):
    type =None

    """

    Events is a list of either:
      * dict with 'time' and 'label'
      * np.array with dtype=[('time', 'float'), ('label, 'U')]

    """

    def __init__(self, all=[]):
        BaseDataSource.__init__(self)

        self.all = all

        s = [ np.min(e['time']) for e in self.all if len(e['time'])>0]
        self._t_start = min(s) if len(s)>0 else 0


    @property
    def nb_channel(self):
        return len(self.all)

    @property
    def t_start(self):
        return self._t_start

    @property
    def t_stop(self):
        return self._t_stop

    def get_channel_name(self, chan=0):
        return self.all[chan]['name']

    def get_size(self, chan=0):
        return self.all[chan]['time'].size






class InMemoryEventSource(BaseEventAndEpoch):
    type = 'Event'

    def __init__(self, all_events=[]):
        BaseEventAndEpoch.__init__(self, all=all_events)
        s = [ np.max(e['time']) for e in self.all  if len(e['time'])>0]
        self._t_stop = max(s) if len(s)>0 else 0


    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        ev_times = self.all[chan]['time'][i_start:i_stop]
        ev_labels = self.all[chan]['label'][i_start:i_stop]
        return ev_times, ev_labels

    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        ev_times = self.all[chan]['time']
        ev_labels = self.all[chan]['label']

        i1 = np.searchsorted(ev_times, t_start, side='left')
        i2 = np.searchsorted(ev_times, t_stop, side='left')
        sl = slice(i1, i2+1)
        return ev_times[sl], ev_labels[sl]
