import ephyviewer

import numpy as np


def make_fake_signals():
    
    signals = np.random.randn(1000000, 16)
    sample_rate = 10000.
    t_start = 0.
    
    source = ephyviewer.InMemoryAnalogSignalSource(signals, sample_rate, t_start)    
    
    
    return source