# -*- coding: utf-8 -*-
"""


"""

from .sourcebase import BaseDataSource
import sys
import logging

import numpy as np

try:
    from distutils.version import LooseVersion as V
    import neo
    if V(neo.__version__)>='0.6.0':
        HAVE_NEO = True
        from neo.rawio.baserawio import BaseRawIO
    else:
        HAVE_NEO = False
        #~ print('neo version is too old', neo.__version__)
except ImportError:
    HAVE_NEO = False

from .signals import BaseAnalogSignalSource
from .events import BaseEventAndEpoch
from .spikes import BaseSpikeSource


logger = logging.getLogger()

#~ print('HAVE_NEO', HAVE_NEO)

class NeoAnalogSignalSource(BaseAnalogSignalSource):
    def __init__(self, neorawio, channel_indexes=None):
        
        BaseAnalogSignalSource.__init__(self)
        self.with_scatter = False
        
        self.neorawio =neorawio
        if channel_indexes is None:
            channel_indexes = slice(None)
        self.channel_indexes = channel_indexes
        self.channels = self.neorawio.header['signal_channels'][channel_indexes]
        self.sample_rate = self.neorawio.get_signal_sampling_rate(channel_indexes=self.channel_indexes)
        
        #TODO: something for multi segment
        self.block_index = 0
        self.seg_index = 0
    
    @property
    def nb_channel(self):
        return len(self.channels)

    def get_channel_name(self, chan=0):
        return self.channels[chan]['name']

    @property
    def t_start(self):
        t_start = self.neorawio.get_signal_t_start(self.block_index, self.seg_index,
                    channel_indexes=self.channel_indexes)
        return t_start

    @property
    def t_stop(self):
        t_stop = self.t_start + self.get_length()/self.sample_rate
        return t_stop
    
    def get_length(self):
        length = self.neorawio.get_signal_size(self.block_index, self.seg_index,
                        channel_indexes=self.channel_indexes)
        return length

    def get_shape(self):
        return (self.get_length(), self.nb_channel)

    def get_chunk(self, i_start=None, i_stop=None):
        sigs = self.neorawio.get_analogsignal_chunk(block_index=self.block_index, seg_index=self.seg_index,
                        i_start=i_start, i_stop=i_stop, channel_indexes=self.channel_indexes)
        #TODO something for scaling
        
        #TODO add an option to pre load evrything in memory for short length
        
        return sigs
        

class NeoSpikeSource(BaseSpikeSource):
    def __init__(self, neorawio, channel_indexes=None):
        self.neorawio =neorawio
        if channel_indexes is None:
            channel_indexes = slice(None)
        self.channel_indexes = channel_indexes
        
        self.channels = self.neorawio.header['unit_channels'][channel_indexes]
        
        #TODO: something for multi segment
        self.block_index = 0
        self.seg_index = 0

    @property
    def nb_channel(self):
        return len(self.channels)

    def get_channel_name(self, chan=0):
        return self.channels[chan]['name']

    @property
    def t_start(self):
        t_start = self.neorawio.segment_t_start(self.block_index, self.seg_index)
        return t_start

    @property
    def t_stop(self):
        t_stop = self.neorawio.segment_t_stop(self.block_index, self.seg_index)
        return t_stop

    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        raise(NotImplementedError)
    
    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        spike_timestamp = self.neorawio.get_spike_timestamps(block_index=self.block_index,
                        seg_index=self.seg_index, unit_index=chan, t_start=t_start, t_stop=t_stop)
        
        spike_times = self.neorawio.rescale_spike_timestamp(spike_timestamp, dtype='float64')
        
        return spike_times

    


class NeoEpochSource(BaseEventAndEpoch):
    def __init__(self, neorawio, channel_indexes=None):
        self.neorawio =neorawio
        if channel_indexes is None:
            channel_indexes = slice(None)
        self.channel_indexes = channel_indexes
        
        self.channels = self.neorawio.header['event_channels'][channel_indexes]
        
        #TODO: something for multi segment
        self.block_index = 0
        self.seg_index = 0
        
        self._cache_event = {}

    @property
    def nb_channel(self):
        return len(self.channels)

    def get_channel_name(self, chan=0):
        return self.channels[chan]['name']

    @property
    def t_start(self):
        t_start = self.neorawio.segment_t_start(self.block_index, self.seg_index)
        return t_start

    @property
    def t_stop(self):
        t_stop = self.neorawio.segment_t_stop(self.block_index, self.seg_index)
        return t_stop

    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        k = (self.block_index , self.seg_index, chan) 
        if k not in self._cache_event:
            self._cache_event[k] = self.get_chunk_by_time(chan=chan,  t_start=None, t_stop=None) 
        
        ep_times, ep_durations, ep_labels = self._cache_event[k]
        
        ep_times = ep_times[i_start:i_stop]
        if ep_durations is not None:
            ep_durations = ep_durations[i_start:i_stop]
        ep_labels = ep_labels[i_start:i_stop]
        
        return ep_times, ep_durations, ep_labels
    
    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        
        ep_timestamps, ep_durations, ep_labels = self.neorawio.get_event_timestamps(block_index=self.block_index,
                        seg_index=self.seg_index, event_channel_index=chan, t_start=t_start, t_stop=t_stop)
        
        ep_times = self.neorawio.rescale_event_timestamp(ep_timestamps, dtype='float64')
        
        if ep_durations is not None:
            ep_durations = self.neorawio.rescale_epoch_duration(ep_durations, dtype='float64')
        else:
            ep_durations = np.zeros_like(ep_times)
        
        return ep_times, ep_durations, ep_labels


    
    
    
def get_source_from_neo(neorawio):
    assert HAVE_NEO
    assert isinstance(neorawio, BaseRawIO)
    
    if neorawio.header is None:
        logger.info('parse header')
        neorawio.parse_header()
    
    sources = {'signal':[], 'epoch':[], 'spike':[]}
    
    if neorawio.signal_channels_count()>0:
        #Signals
        for channel_indexes in neorawio.get_group_channel_indexes():
            #one soure by channel group
            sources['signal'].append(NeoAnalogSignalSource(neorawio, channel_indexes))
            
        
    
    if neorawio.unit_channels_count()>0:
        #Spikes: TODO
        sources['spike'].append(NeoSpikeSource(neorawio, None))
    
    
    if neorawio.event_channels_count()>0:
        sources['epoch'].append(NeoEpochSource(neorawio, None))
        
    
    
    return sources
    
    