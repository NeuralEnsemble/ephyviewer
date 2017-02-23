# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

from .sourcebase import BaseDataSource



class EventSource(BaseDataSource):
    type = 'Event'
    
    """
    
    Events is a list of either:
      * dict with 'time' and 'label'
      * np.array with dtype=[('time', 'float'), ('label, 'U')]
    
    """
    
    def __init__(self, all_events=[]):
        BaseDataSource.__init__(self)
        
        self.all_events = all_events
        
        self._t_start = min([ np.min(events['time']) for events in self.all_events])
        self._t_stop = max([ np.max(events['time']) for events in self.all_events])

    @property
    def nb_channel(self):
        return len(self.all_events)

    def get_t_start(self, seg_num=0):
        assert seg_num==0
        return self._t_start

    def get_t_stop(self, seg_num=0):
        assert seg_num==0
        return self._t_stop
