# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .sourcebase import BaseDataSource
from .events import BaseInMemoryEventAndEpoch



class InMemoryEpochSource(BaseInMemoryEventAndEpoch):
    type = 'Epoch'
    
    def __init__(self, all_epochs=[]):
        BaseInMemoryEventAndEpoch.__init__(self, all=all_epochs)
        self._t_stop = max([ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0])

    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        ep_times = self.all[chan]['time'][i_start:i_stop]
        ep_durations = self.all[chan]['duration'][i_start:i_stop]
        ep_labels = self.all[chan]['label'][i_start:i_stop]
        return ep_times, ep_durations, ep_labels
    
    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        ev_times = self.all[chan]['time']
        ep_durations = self.all[chan]['duration']
        ev_labels = self.all[chan]['label']
        
        keep1 = (ev_times>=t_start) & (ev_times<t_stop)#begin inside
        keep2 = (ev_times+ep_durations>=t_start) & (ev_times+ep_durations<t_stop) #end inside
        keep3 = (ev_times<=t_start) & (ev_times+ep_durations>t_stop) # overlap
        keep = keep1|  keep2 | keep3
        
        return ev_times[keep], ep_durations[keep], ev_labels[keep]


