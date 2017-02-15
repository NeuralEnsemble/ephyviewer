import ephyviewer
import numpy as np


def test_InMemoryAnalogSignalSource():
    
    signals = np.random.randn(1000000, 16)
    sample_rate = 10000.
    t_start = 0.
    
    source = ephyviewer.InMemoryAnalogSignalSource(signals, sample_rate, t_start)
    
    assert source.nb_segment==1
    assert source.nb_channel==16
    assert source.get_shape() == signals.shape
    assert np.all(source.get_chunk(i_start=50, i_stop=55) == signals[50:55])
    
    
    
    
if __name__=='__main__':
    test_InMemoryAnalogSignalSource()