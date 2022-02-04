import pytest

import ephyviewer
import numpy as np
import os

# get_tdt_test_files
from  ephyviewer.tests.testing_tools import make_video_file, get_blackrock_files


def test_InMemoryAnalogSignalSource():

    signals = np.random.randn(1000000, 16)
    sample_rate = 10000.
    t_start = 0.

    source = ephyviewer.InMemoryAnalogSignalSource(signals, sample_rate, t_start)

    assert source.nb_channel==16
    assert source.get_shape() == signals.shape
    assert np.all(source.get_chunk(i_start=50, i_stop=55) == signals[50:55])






def test_VideoMultiFileSource():
    import av

    #~ video_filenames = ['video0.avi', 'video1.avi', 'video2.avi',]
    video_filenames = ['video0.avi',]
    for filename in video_filenames:
        if not os.path.exists(filename):
            make_video_file(filename)

    videotimes = None
    source = ephyviewer.MultiVideoFileSource(video_filenames, videotimes)
    assert source.t_start==0
    assert source.t_stop==10.


def test_InMemoryEventSource():
    ev_times = np.arange(0, 10., .5)
    ev_labels = np.array(['Event0 num {}'.format(i) for i in range(ev_times.size)], dtype='U')
    event0 = { 'time':ev_times, 'label':ev_labels, 'name':  'Event0' }

    ev_times = np.arange(-6, 8., 2.)
    ev_labels = np.array(['Event1 num {}'.format(i) for i in range(ev_times.size)], dtype='U')
    event1 = { 'time':ev_times, 'label':ev_labels, 'name':  'Event1' }

    all_events = [event0, event1]

    source = ephyviewer.InMemoryEventSource(all_events=all_events)

    assert source.t_start==-6.
    assert source.t_stop==9.5
    assert source.get_size(0)==20


def test_InMemoryEpochSource():
    ep_times = np.arange(0, 10., .5)
    ep_durations = np.ones(ep_times.shape) * .1
    ep_labels = np.array(['Epoch0 num {}'.format(i) for i in range(ep_times.size)], dtype='U')
    epoch0 = { 'time':ep_times, 'duration':ep_durations,'label':ep_labels, 'name':  'Epoch0' }

    ep_times = np.arange(-6, 8., 2.)
    ep_durations = np.ones(ep_times.shape) * .2
    ep_labels = np.array(['Epoch1 num {}'.format(i) for i in range(ep_times.size)], dtype='U')
    epoch1 = { 'time':ep_times, 'duration':ep_durations, 'label':ep_labels, 'name':  'Epoch1' }

    all_epochs = [epoch0, epoch1]

    source = ephyviewer.InMemoryEpochSource(all_epochs=all_epochs)

    assert source.t_start==-6.
    assert source.t_stop==9.6
    assert source.get_size(0)==20


def test_spikesource():
    sike_times = np.arange(0, 10., .5)
    spikes0 = { 'time':sike_times, 'name':  'Unit#0' }

    sike_times = np.arange(-6, 8., 2.)
    spikes1 = { 'time':sike_times, 'name':  'unit#1' }

    all_spikes = [spikes0, spikes1]

    source = ephyviewer.InMemorySpikeSource(all_spikes=all_spikes)

    assert source.t_start==-6.
    assert source.t_stop==9.5
    assert source.get_size(0)==20



def test_neo_rawio_sources():
    #~ from neo.rawio.tdtrawio import TdtRawIO
    #~ local_tdt_folder = get_tdt_test_files()
    #~ neorawio = TdtRawIO(dirname=local_tdt_folder)
    #~ neorawio.parse_header()
    #~ print(neorawio)

    from neo.rawio.blackrockrawio import BlackrockRawIO
    filename = get_blackrock_files()
    neorawio = BlackrockRawIO(filename=filename)
    neorawio.parse_header()
    print(neorawio)


    sources = ephyviewer.get_sources_from_neo_rawio(neorawio)
    #~ print(sources)

    for s in sources['signal']:
        print(s.t_start, s.nb_channel, s.sample_rate)
        print(s.get_chunk(i_start=0, i_stop=1024).shape)

    for s in sources['epoch']:
        print(s.t_start, s.nb_channel)
        #~ print(s.get_chunk(i_start=0, i_stop=1024).shape)
        print(s.get_chunk_by_time(chan=0,  t_start=None, t_stop=None))

    for s in sources['spike']:
        print(s.t_start, s.nb_channel)
        print(s.get_chunk_by_time(chan=0,  t_start=None, t_stop=None))
        #~ print(s.get_chunk(i_start=0, i_stop=1024).shape)

def test_neo_object_sources():

    from neo.test.generate_datasets import generate_one_simple_segment
    import neo

    neo_seg = generate_one_simple_segment(supported_objects=[neo.Segment, neo.AnalogSignal, neo.Event, neo.Epoch, neo.SpikeTrain])

    sources = ephyviewer.get_sources_from_neo_segment(neo_seg)


    for s in sources['signal']:
        print(s.t_start, s.nb_channel, s.sample_rate)
        print(s.get_chunk(i_start=0, i_stop=1024).shape)

    for s in sources['epoch']:
        print(s.t_start, s.nb_channel)
        print(s.get_chunk_by_time(chan=0,  t_start=0, t_stop=10.))

    for s in sources['event']:
        print(s.t_start, s.nb_channel)
        print(s.get_chunk_by_time(chan=0,  t_start=0, t_stop=10.))

    for s in sources['spike']:
        print(s.t_start, s.nb_channel)
        print(s.get_chunk_by_time(chan=0,  t_start=0., t_stop=10.))
        #~ print(s.get_chunk(i_start=0, i_stop=1024).shape)


def test_spikeinterface_sources():
    import spikeinterface as si
    from spikeinterface.core.testing_tools import generate_recording, generate_sorting

    recording = generate_recording()
    source = ephyviewer.SpikeInterfaceRecordingSource(recording=recording)
    print(source)

    print(source.t_start, source.nb_channel, source.sample_rate)

    sorting = generate_sorting()
    source = ephyviewer.SpikeInterfaceSortingSource(sorting=sorting)
    print(source)

    print(source.t_start, source.nb_channel, source.get_channel_name())




if __name__=='__main__':
    test_InMemoryAnalogSignalSource()
    test_VideoMultiFileSource()
    test_InMemoryEventSource()
    test_InMemoryEpochSource()
    test_spikesource()
    test_neo_rawio_sources()
    test_neo_object_sources()
    test_spikeinterface_sources()
