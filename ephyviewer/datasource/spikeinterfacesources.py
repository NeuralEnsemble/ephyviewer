"""
Data sources for SpikeInterface
"""

from .sourcebase import BaseDataSource
import sys
import logging

from packaging.version import Version as V

import numpy as np

try:
    import spikeinterface
    if V(spikeinterface.__version__)>=V('0.90.1'):
        HAVE_SI = True
    else:
        HAVE_SI = False
except ImportError:
    HAVE_SI = False


from .signals import BaseAnalogSignalSource
from .spikes import BaseSpikeSource


class SpikeInterfaceRecordingSource(BaseAnalogSignalSource):
    def __init__(self, recording, segment_index=0):
        BaseAnalogSignalSource.__init__(self)

        self.recording = recording
        self.segment_index = segment_index

        self._nb_channel = self.recording.get_num_channels()
        self.sample_rate = self.recording.get_sampling_frequency()

    @property
    def nb_channel(self):
        return self._nb_channel

    def get_channel_name(self, chan=0):
        return str(self.recording.channel_ids[chan])

    @property
    def t_start(self):
        return self.recording.sample_index_to_time(0, segment_index=self.segment_index)

    @property
    def t_stop(self):
        return self.recording.sample_index_to_time(self.get_length() - 1, segment_index=self.segment_index)

    def get_length(self):
        return self.recording.get_num_samples(segment_index=self.segment_index)

    def get_shape(self):
        return (self.get_length(),self.nb_channel)

    def get_chunk(self, i_start=None, i_stop=None):
        traces = self.recording.get_traces(segment_index=self.segment_index, start_frame=i_start, end_frame=i_stop)
        return traces

    def time_to_index(self, t):
        return int(self.recording.time_to_sample_index(t, segment_index=self.segment_index))

    def index_to_time(self, ind):
        return float(self.recording.sample_index_to_time(ind, segment_index=self.segment_index))



class SpikeInterfaceSortingSource(BaseSpikeSource):
    def __init__(self, sorting, segment_index=0):
        BaseSpikeSource.__init__(self)

        self.sorting = sorting
        self.segment_index = segment_index

        #TODO: no way to know the duration without a registered recording
        self._t_stop = 10.

    @property
    def nb_channel(self):
        return len(self.sorting.unit_ids)

    def get_channel_name(self, chan=0):
        return str(self.sorting.unit_ids[chan])

    @property
    def t_start(self):
        return self.sorting.sample_index_to_time(0, segment_index=self.segment_index)

    @property
    def t_stop(self):
        if self.sorting.has_recording():
            return self.sorting.get_total_duration()
        return self._t_stop

    def get_chunk(self, chan=0,  i_start=None, i_stop=None):
        unit_id = self.sorting.unit_ids[chan]
        spike_frames = self.sorting.get_unit_spike_train(unit_id,
                    segment_index=self.segment_index, start_frame=i_start, end_frame=i_stop)
        spike_frames = spike_frames[i_start:i_stop]
        spike_times = self.sorting.sample_index_to_time(spike_frames, segment_index=self.segment_index)
        return spike_times

    def get_chunk_by_time(self, chan=0,  t_start=None, t_stop=None):
        spike_times = self.get_chunk(chan=chan)
        i1 = np.searchsorted(spike_times, t_start, side='left')
        i2 = np.searchsorted(spike_times, t_stop, side='left')
        sl = slice(i1, i2+1)
        return spike_times[sl]
