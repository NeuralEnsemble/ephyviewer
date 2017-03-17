# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)
import numpy as np

import matplotlib.cm
import matplotlib.colors


from .sourcebase import BaseDataSource
from .events import BaseInMemoryEventAndEpoch



class InMemoryEpochSource(BaseInMemoryEventAndEpoch):
    type = 'Epoch'
    
    def __init__(self, all_epochs=[]):
        BaseInMemoryEventAndEpoch.__init__(self, all=all_epochs)
        
        s = [ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0]
        self._t_stop = max(s) if len(s)>0 else 0


    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        ep_times = self.all[chan]['time'][i_start:i_stop]
        ep_durations = self.all[chan]['duration'][i_start:i_stop]
        ep_labels = self.all[chan]['label'][i_start:i_stop]
        return ep_times, ep_durations, ep_labels
    
    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        ep_times = self.all[chan]['time']
        ep_durations = self.all[chan]['duration']
        ep_labels = self.all[chan]['label']
        
        #~ keep1 = (ep_times>=t_start) & (ep_times<t_stop)#begin inside
        #~ keep2 = (ep_times+ep_durations>=t_start) & (ep_times+ep_duqrations<t_stop) #end inside
        #~ keep3 = (ep_times<=t_start) & (ep_times+ep_durations>t_stop) # overlap
        #~ keep = keep1|  keep2 | keep3
        
        #~ return ep_times[keep], ep_durations[keep], ep_labels[keep]
        
        i1 = np.searchsorted(ep_times, t_start, side='left')
        i2 = np.searchsorted(ep_times+ep_durations, t_stop, side='left')
        sl = slice(max(0, i1-1), i2+1)
        return ep_times[sl], ep_durations[sl], ep_labels[sl]




class WritableEpochSource(InMemoryEpochSource):
    """
    Identique to EpochSource but onlye one channel that can be persosently saved.
    
    epoch is dict
    { 'time':np.array, 'duration':np.array, 'label':np.array, 'name':' ''}
    """
    def __init__(self, epoch, possible_labels, color_labels=None):
        InMemoryEpochSource.__init__(self, all_epochs=[epoch])
        
        #~ self._t_stop = max([ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0])
        
        self.times = self.all[0]['time']
        self.durations = self.all[0]['duration']
        
        assert np.all((self.times[:-1]+self.durations[:-1])<=self.times[1:])
        
        assert np.all(np.in1d(epoch['label'], possible_labels))
        self.possible_labels = possible_labels
        
        if color_labels is None:
            n = len(possible_labels)
            cmap = matplotlib.cm.get_cmap('Dark2' , n)
            color_labels = [ matplotlib.colors.ColorConverter().to_rgb(cmap(i)) for i in  range(n)]
            color_labels = (np.array(color_labels)*255).astype(int)
            color_labels = color_labels.tolist()
        self.color_labels = color_labels
        self.label_to_color = dict(zip(self.possible_labels, self.color_labels))
        
    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        assert chan==0
        return InMemoryEpochSource. get_chunk(self, chan=chan,  i_start=i_start, i_stop=i_stop)
    
    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        #~ print(chan)
        assert chan==0
        return InMemoryEpochSource.get_chunk_by_time(self, chan=chan,  t_start=t_start, t_stop=t_stop)
    
    def color_by_label(self, label):
        return self.label_to_color[label]


    def _clean_and_set(self,ep_times, ep_durations, ep_labels):
        keep = ep_durations>0.
        ep_times = ep_times[keep]
        ep_durations = ep_durations[keep]
        ep_labels = ep_labels[keep]
        
        self.all[0]['time'] = ep_times
        self.all[0]['duration'] = ep_durations
        self.all[0]['label'] = ep_labels

    
    def add_epoch(self, t, duration, label):
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        
        ind = np.searchsorted(ep_times, t, side='left')
        
        ep_times = insert_item(ep_times, ind, t)
        ep_durations = insert_item(ep_durations, ind, duration)
        ep_labels = insert_item(ep_labels, ind, label)
        
        #previous
        prev = ind-1
        while prev>=0:
            if (ep_times[prev]+ep_durations[prev])>ep_times[ind]:
                ep_durations[prev] = ep_times[ind] - ep_times[prev]
            else:
                break
            prev = prev-1
        
        #nexts
        next = ind+1
        while next<ep_times.size:
            delta = (ep_times[ind]+ep_durations[ind]) - ep_times[next]
            if delta>0:
                ep_times[next] += delta
                ep_durations[next] -= delta
            else:
                break
            next = next + 1
        
        self._clean_and_set(ep_times, ep_durations, ep_labels)
        
    def merge_neighbors(self):
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        
        mask = ((ep_times[:-1] + ep_durations[:-1])==ep_times[1:]) & (ep_labels[:-1]==ep_labels[1:])
        inds, = np.nonzero(mask)
        
        for ind in inds:
            ep_times[ind+1] = ep_times[ind]
            ep_durations[ind+1] = ep_durations[ind] + ep_durations[ind+1]
            ep_durations[ind] = -1
        
        self._clean_and_set(ep_times, ep_durations, ep_labels)
    
    def fill_blank(self, method='from_left'):
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        
        mask = ((ep_times[:-1] + ep_durations[:-1])<ep_times[1:])
        inds,  = np.nonzero(mask)
        
        if method=='from_left':
            for ind in inds:
                ep_durations[ind] = ep_times[ind+1] - ep_times[ind]
                
        elif method=='from_right':
            for ind in inds:
                gap = ep_times[ind+1] - (ep_times[ind] + ep_durations[ind])
                ep_times[ind+1] -= gap
                ep_durations[ind+1] += gap
                
        elif method=='from_nearest':
            for ind in inds:
                gap = ep_times[ind+1] - (ep_times[ind] + ep_durations[ind])
                ep_durations[ind] += gap/2.
                ep_times[ind+1] -= gap/2.
                ep_durations[ind+1] += gap/2.
                
        
        self._clean_and_set(ep_times, ep_durations, ep_labels)
    
    def save(self):
        print('WritableEpochSource.save')
    


        
        


def insert_item(arr, ind, value):
    new_arr = np.zeros(arr.size+1, dtype=arr.dtype)
    
    new_arr[:ind] = arr[:ind]
    new_arr[ind] = value
    new_arr[ind+1:] = arr[ind:]
    
    return new_arr
