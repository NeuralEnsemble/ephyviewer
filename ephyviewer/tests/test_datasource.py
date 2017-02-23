
import ephyviewer
import numpy as np
import os

from  ephyviewer.tests.testing_tools import make_video_file


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
    
    video_filenames = ['video0.avi', 'video1.avi', 'video2.avi',]
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
    
    
    
    
if __name__=='__main__':
    #~ test_InMemoryAnalogSignalSource()
    #~ test_VideoMultiFileSource()
    #~ test_InMemoryEventSource()
    test_InMemoryEpochSource()

