import ephyviewer
import numpy as np
import os

from  ephyviewer.tests.testing_tools import make_video_file


def test_InMemoryAnalogSignalSource():
    
    signals = np.random.randn(1000000, 16)
    sample_rate = 10000.
    t_start = 0.
    
    source = ephyviewer.InMemoryAnalogSignalSource(signals, sample_rate, t_start)
    
    assert source.nb_segment==1
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
    assert source.get_t_start()==0
    print(source.get_t_stop())
    assert source.get_t_stop()==10.
    
    
    
    
    
    
    
    
    
if __name__=='__main__':
    #~ test_InMemoryAnalogSignalSource()
    test_VideoMultiFileSource()