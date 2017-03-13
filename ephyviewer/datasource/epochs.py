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
        self._t_stop = max([ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0])

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
        sl = slice(i1, i2+1)
        return ep_times[sl], ep_durations[sl], ep_labels[sl]




class WritableEpochSource(InMemoryEpochSource):
    """
    Identique to EpochSource but onlye one channel that can be persosently saved.
    
    epoch is dict
    { 'time':np.array, 'duration':np.array, 'label':np.array, 'name':' ''}
    """
    def __init__(self, epoch, possible_labels, color_labels=None):
        InMemoryEpochSource.__init__(self, all_epochs=[epoch])
        self._t_stop = max([ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0])
        
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
        print(chan)
        assert chan==0
        return InMemoryEpochSource.get_chunk_by_time(self, chan=chan,  t_start=t_start, t_stop=t_stop)
    
    def color_by_label(self, label):
        return self.label_to_color[label]

    def add_epoch(self, t, duration, label):
        print('WritableEpochSource.add_epoch', t, duration, label)
        
        ep_times = self.all[0]['time']
        ep_durations = self.all[0]['duration']
        ep_labels = self.all[0]['label']
        
        ind = np.searchsorted(ep_times, t, side='left')
        #~ print('ind', ind, ep_times[ind], ep_times[ind+1])
        ind = ind
        print('ind', ind)
        
        
        new_times = insert_item(ep_times, ind, t)
        new_durations = insert_item(ep_durations, ind, duration)
        new_labels = insert_item(ep_labels, ind, label)
        
        print(new_times)
        print(new_durations)
        
        
        #previous
        prev = ind-1
        if prev>=0 and (new_times[prev]+new_durations[prev])>new_times[ind]:
            print('prev', prev, new_times[prev], new_durations[prev], new_times[ind])
            new_durations[prev] = new_times[ind] - new_times[prev]
            print(prev, new_durations[prev])
        
        #nexts
        next = ind+1
        while next<new_times.size:
            print('*')
            print('next', next)
            delta = (new_times[ind]+new_durations[ind]) - new_times[next]
            if delta>0:
                print('next', next, new_times[ind],new_durations[ind],new_times[next], 'delta', delta)
                new_times[next] += delta
                new_durations[next] -= delta
            else:
                break
            next = next + 1

        
        print('---')
        print(new_times)
        print(new_durations)
        
        keep = new_durations>0.
        print('remove', np.nonzero(~keep))
        new_times = new_times[keep]
        new_durations = new_durations[keep]
        new_labels = new_labels[keep]
        print('======')
        print(new_times)
        print(new_durations)
        print()
        
        self.all[0]['time'] = new_times
        self.all[0]['duration'] = new_durations
        self.all[0]['label'] = new_labels


def insert_item(arr, ind, value):
    new_arr = np.zeros(arr.size+1, dtype=arr.dtype)
    
    new_arr[:ind] = arr[:ind]
    new_arr[ind] = value
    new_arr[ind+1:] = arr[ind:]
    
    return new_arr
