# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import ephyviewer

import numpy as np


def make_fake_signals():
    
    signals = np.random.randn(1000000, 16)
    
    signals *= np.random.rand(16)[None,:]
    signals += (np.random.rand(16)[None,:]-1)*3
    
    
    sample_rate = 10000.
    t_start = 0.
    
    source = ephyviewer.InMemoryAnalogSignalSource(signals, sample_rate, t_start)    
    
    
    return source



def make_video_file(filename, codec='mpeg4', rate=25.):
    print('make_video_file', filename)
    
    import av
    output = av.open(filename, 'w')
    stream = output.add_stream(codec, rate)
    stream.bit_rate = 8000000
    stream.pix_fmt = 'yuv420p'
    stream.height = 600
    stream.width = 800
    
    duration = 10.
    
    
    one_img = np.ones((stream.height, stream.width), dtype='u1, u1, u1')
    for i in range(int(duration*rate)):
        frame = av.VideoFrame.from_ndarray(one_img, format='bgr24')
        packet = stream.encode(frame)
        output.mux(packet)
    
    
    output.close()


def make_fake_video_source():
    filename = 'video0.avi'
    if not os.path.exists(filename):
        make_video_file(filename)
    
    
    source = ephyviewer.MultiVideoFileSource([filename])
    
    return source
    
    
