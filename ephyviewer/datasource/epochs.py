# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)
import os
import numpy as np

import matplotlib.cm
import matplotlib.colors

try:
    import pandas as pd
    HAVE_PANDAS = True
except ImportError:
    HAVE_PANDAS = False


from .sourcebase import BaseDataSource
from .events import BaseEventAndEpoch



class InMemoryEpochSource(BaseEventAndEpoch):
    type = 'Epoch'
    
    def __init__(self, all_epochs=[]):
        BaseEventAndEpoch.__init__(self, all=all_epochs)
        
        s = [ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0]
        self._t_stop = max(s) if len(s)>0 else 0


    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        ep_times = self.all[chan]['time'][i_start:i_stop]
        ep_durations = self.all[chan]['duration'][i_start:i_stop]
        ep_labels = self.all[chan]['label'][i_start:i_stop]
        ep_ids = np.arange(len(ep_times))[i_start:i_stop]
        return ep_times, ep_durations, ep_labels, ep_ids
    
    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        ep_times = self.all[chan]['time']
        ep_durations = self.all[chan]['duration']
        ep_labels = self.all[chan]['label']
        ep_ids = np.arange(len(ep_times))
        
        keep1 = (ep_times>=t_start) & (ep_times<t_stop) # epochs that start inside range
        keep2 = (ep_times+ep_durations>=t_start) & (ep_times+ep_durations<t_stop) # epochs that end inside range
        keep3 = (ep_times<=t_start) & (ep_times+ep_durations>t_stop) # epochs that span the range
        keep = keep1 | keep2 | keep3
        
        return ep_times[keep], ep_durations[keep], ep_labels[keep], ep_ids[keep]




class WritableEpochSource(InMemoryEpochSource):
    """
    Identique to EpochSource but onlye one channel that can be persisently saved.
    
    epoch is dict
    { 'time':np.array, 'duration':np.array, 'label':np.array, 'name':' ''}
    """
    def __init__(self, epoch=None, possible_labels=[], color_labels=None, channel_name=''):
        
        self.possible_labels = possible_labels
        self.channel_name = channel_name
        
        if epoch is None:
            epoch = self.load()
        
        InMemoryEpochSource.__init__(self, all_epochs=[epoch])
        
        #~ self._t_stop = max([ np.max(e['time']+e['duration']) for e in self.all if len(e['time'])>0])
        
        self.times = self.all[0]['time']
        self.durations = self.all[0]['duration']
        
        assert self.all[0]['time'].dtype.kind=='f'
        assert self.all[0]['duration'].dtype.kind=='f'
        
        assert np.all(np.in1d(epoch['label'], self.possible_labels))
        
        if color_labels is None:
            n = len(self.possible_labels)
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
        
        # remove bad epochs
        keep = ep_durations >= 1e-6 # discard epochs shorter than 1 microsecond or with negative duration
        ep_times = ep_times[keep]
        ep_durations = ep_durations[keep]
        ep_labels = ep_labels[keep]
        
        # sort epochs by start time
        ordering = np.argsort(ep_times)
        ep_times = ep_times[ordering]
        ep_durations = ep_durations[ordering]
        ep_labels = ep_labels[ordering]
        
        # set epochs for the WritableEpochSource
        self.all[0]['time'] = ep_times
        self.all[0]['duration'] = ep_durations
        self.all[0]['label'] = ep_labels
    
    def add_epoch(self, t1, duration, label):
        
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        ep_times = np.append(ep_times, t1)
        ep_durations = np.append(ep_durations, duration)
        ep_labels = np.append(ep_labels, label)
        
        self._clean_and_set(ep_times, ep_durations, ep_labels)
    
    def change_labels(self, new_labels):
        
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        assert(ep_labels.size == new_labels.size)
        ep_labels = new_labels
        self._clean_and_set(ep_times, ep_durations, ep_labels)
    
    def delete_in_between(self, t1, t2):
        
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        ep_stops = ep_times + ep_durations
        
        for i in range(len(ep_times)):
            
            # if epoch starts and ends inside range, delete it
            if ep_times[i]>=t1 and ep_stops[i]<=t2:
                ep_durations[i] = -1 # non-positive duration flags this epoch for clean up
            
            # if epoch starts before and ends inside range, truncate it
            elif ep_times[i]<t1 and (t1<ep_stops[i]<=t2):
                ep_durations[i] = t1 - ep_times[i]
            
            # if epoch starts inside and ends after range, truncate it
            elif (t1<=ep_times[i]<t2) and ep_stops[i]>t2:
                ep_durations[i] = ep_stops[i] - t2
                ep_times[i] = t2
            
            # if epoch starts before and ends after range,
            # truncate the first part and add a new epoch for the end part
            elif ep_times[i]<=t1 and ep_stops[i]>=t2:
                ep_durations[i] = t1 - ep_times[i]
                ep_times = np.append(ep_times, t2)
                ep_durations = np.append(ep_durations, ep_stops[i]-t2)
                ep_labels = np.append(ep_labels, ep_labels[i])
        
        self._clean_and_set(ep_times, ep_durations, ep_labels)
    
    def merge_neighbors(self):
        
        ep_times, ep_durations, ep_labels = self.all[0]['time'], self.all[0]['duration'], self.all[0]['label']
        ep_stops = ep_times + ep_durations
        
        for label in self.possible_labels:
            inds, = np.nonzero(ep_labels == label)
            for i in range(len(inds)-1):
                
                # if two sequentially adjacent epochs with the same label
                # overlap or have less than 1 microsecond separation, merge them
                if ep_times[inds[i+1]] - ep_stops[inds[i]] < 1e-6:
                    
                    # stretch the second epoch to cover the range of both epochs
                    ep_times[inds[i+1]] = min(ep_times[inds[i]], ep_times[inds[i+1]])
                    ep_stops[inds[i+1]] = max(ep_stops[inds[i]], ep_stops[inds[i+1]])
                    ep_durations[inds[i+1]] = ep_stops[inds[i+1]] - ep_times[inds[i+1]]
                    
                    # delete the first epoch
                    ep_durations[inds[i]] = -1 # non-positive duration flags this epoch for clean up
        
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
    
    def load(self):
        """
        Returns a dictionary containing the data for an epoch.
        
        Derived subclasses of WritableEpochSource override this method to
        implement loading a file or importing data from objects in memory. The
        superclass implementation WritableEpochSource.load() creates an empty
        dictionary with the correct keys and types. It can be called from the
        subclass implementation using super().load() if, for example, the file
        to be loaded does not exist.
        
        The method returns a dictionary containing the loaded data in this form:
        
        { 'time': np.array, 'duration': np.array, 'label': np.array, 'name': string }
        """
        
        s = max([len(l) for l in self.possible_labels])
        epoch = {'time':     np.array([], dtype='float64'),
                 'duration': np.array([], dtype='float64'),
                 'label':    np.array([], dtype='U'+str(s)),
                 'name':     self.channel_name}
        return epoch
    
    def save(self):
        print('WritableEpochSource.save')
        raise NotImplementedError()
    


class CsvEpochSource(WritableEpochSource):
    def __init__(self, filename, possible_labels, color_labels=None, channel_name=''):
        assert HAVE_PANDAS, 'Pandas is not installed'
        
        self.filename = filename
        
        WritableEpochSource.__init__(self, epoch=None, possible_labels=possible_labels, color_labels=color_labels, channel_name=channel_name)
        
    def load(self):
        """
        Returns a dictionary containing the data for an epoch.
        
        Data is loaded from the CSV file if it exists; otherwise the superclass
        implementation in WritableEpochSource.load() is called to create an
        empty dictionary with the correct keys and types.
        
        The method returns a dictionary containing the loaded data in this form:
        
        { 'time': np.array, 'duration': np.array, 'label': np.array, 'name': string }
        """
        
        if os.path.exists(self.filename):
            # if file already exists, load previous epoch
            df = pd.read_csv(self.filename,  index_col=None)
            epoch = {'time':     df['time'].values,
                     'duration': df['duration'].values,
                     'label':    df['label'].values,
                     'name':     self.channel_name}
        else:
            # if file does NOT already exist, use superclass method for creating
            # an empty dictionary
            epoch = super().load()
        
        return epoch

    def save(self):
        df = pd.DataFrame()
        df['time'] = np.round(self.all[0]['time'], 6)         # round to nearest microsecond
        df['duration'] = np.round(self.all[0]['duration'], 6) # round to nearest microsecond
        df['label'] = self.all[0]['label']
        df.to_csv(self.filename, index=False)




def insert_item(arr, ind, value):
    new_arr = np.zeros(arr.size+1, dtype=arr.dtype)
    
    new_arr[:ind] = arr[:ind]
    new_arr[ind] = value
    new_arr[ind+1:] = arr[ind:]
    
    return new_arr
