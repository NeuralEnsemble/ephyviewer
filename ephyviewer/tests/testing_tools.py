# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import ephyviewer
import os

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from urllib.request import urlopen


def make_fake_signals():
    np.random.seed(2205)
    signals = np.random.randn(1000000, 16)

    signals *= np.random.rand(16)[None,:]
    signals += (np.random.rand(16)[None,:]-1)*3

    #~ print(signals.shape)
    sample_rate = 10000.
    t_start = 0.

    source = ephyviewer.InMemoryAnalogSignalSource(signals, sample_rate, t_start)


    return source


def make_fake_signals_with_scatter():
    sample_rate = 10000.
    t_start = 0.
    times = np.arange(1000000)/sample_rate
    signals = np.sin(times*2*np.pi*5)[:, None]

    s0 = signals[:-2, 0]
    s1 = signals[1:-1,0]
    s2 = signals[2:,0]

    peaks0,  = np.nonzero((s0<s1) & (s2<s1))
    peaks1,  = np.nonzero((s0>s1) & (s2>s1))

    scatter_indexes = {0: peaks0, 1: peaks1}
    scatter_channels = {0: [0], 1: [0]}
    source = ephyviewer.AnalogSignalSourceWithScatter(signals, sample_rate, t_start, scatter_indexes, scatter_channels)

    return source




def make_video_file(filename, codec='mpeg4', rate=25.): # mpeg4 mjpeg libx264
    print('make_video_file', filename)
    name=filename.replace('.avi', '')
    import av

    w, h = 800, 600

    output = av.open(filename, 'w')
    stream = output.add_stream(codec, rate)
    #~ stream.bit_rate = 8000000
    #~ stream.pix_fmt = 'yuv420p'
    stream.pix_fmt = 'yuv420p'
    stream.height = h
    stream.width = w

    duration = 10.


    #~ one_img = np.ones((h, w, 3), dtype='u1')
    #~ fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=100,)
    fig = plt.figure(figsize=(w/100, h/100), dpi=100,)
    #~ line, = ax.plot([0], [0], marker='o', markersize=50, color='m')
    #~ ax.set_xlim(-1,1)
    #~ ax.set_ylim(-1,1)
    for i in range(int(duration*rate)):
        fig.clear()
        #~ one_img += np.random.randint(low=0, high=255, size=(h, w, 3)).astype('u1')
        text = '{} - frame {:5} - time {:6.3f}s'.format(name, i, i/rate)
        fig.text(.5, .5, text, ha='center', va='center')
        #~ ax.set_title()
        #~ line.set_markersize(i)
        fig.canvas.draw()
        one_img = np.asarray(fig.canvas.buffer_rgba())[:,:,:3]
        one_img = one_img[:,:,::-1].copy()
        #~ one_img = one_img .swapaxes(0,1).copy()

        frame = av.VideoFrame.from_ndarray(one_img, format='bgr24')
        packet = stream.encode(frame)
        if packet is not None:
            output.mux(packet)

    while True :
        try:
            packet = stream.encode(None)
            if packet is None:
                break
            output.mux(packet)
        except av.AVError:
            break

    output.close()


def make_fake_video_source():
    filenames = ['video0.avi', 'video1.avi', 'video2.avi',]
    #~ filenames = ['video0.avi']
    for filename in filenames:
        if not os.path.exists(filename):
            make_video_file(filename, )



    source = ephyviewer.MultiVideoFileSource(filenames)

    return source



def make_fake_event_source():
    all_events = []
    for c in range(3):
        ev_times = np.arange(0, 10., .5) + c*3
        ev_labels = np.array(['Event{} num {}'.format(c, i) for i in range(ev_times.size)], dtype='U')
        all_events.append({ 'time':ev_times, 'label':ev_labels, 'name':'Event{}'.format(c) })

    source = ephyviewer.InMemoryEventSource(all_events=all_events)
    return source



def make_fake_epoch_source():
    all_epochs = []
    for c in range(3):
        ep_times = np.arange(0, 10., .5) + c*3
        ep_durations = np.ones(ep_times.shape) * .1
        ep_labels = np.array(['Event{} num {}'.format(c, i) for i in range(ep_times.size)], dtype='U')
        all_epochs.append({ 'time':ep_times, 'duration':ep_durations, 'label':ep_labels, 'name':'Event{}'.format(c) })

    source = ephyviewer.InMemoryEpochSource(all_epochs=all_epochs)
    return source


def make_fake_spiketrain_source():
    all_spikes =[]
    for c in range(30):
        spike_times = np.arange(0, 10., .5) + c*0.2
        all_spikes.append({ 'time':spike_times, 'name':'Unit#{}'.format(c) })

    source = ephyviewer.InMemorySpikeSource(all_spikes=all_spikes)
    return source


def get_tdt_test_files():
    # this implementation is based on datalad which is buggy on GH actions
    # from neo.utils import download_dataset
    # local_folder = download_dataset(remote_path='tdt/aep_05')
    # return str(local_folder)

    # we use old implementation with http
    url_for_tests = "https://web.gin.g-node.org/NeuralEnsemble/ephy_testing_data/raw/master/"

    files_to_download = [
        'tdt/aep_05/Block-1/aep_05_Block-1.Tbk',
        'tdt/aep_05/Block-1/aep_05_Block-1.Tdx',
        'tdt/aep_05/Block-1/aep_05_Block-1.tev',
        'tdt/aep_05/Block-1/aep_05_Block-1.tsq',
    ]

    local_folder = Path.home() / 'ephy_testing_data_http'

    for file in files_to_download:
        localfile = local_folder / file
        distantfile = url_for_tests + file
        if not localfile.is_file():
            localfile.parent.mkdir(exist_ok=True, parents=True)
            dist = urlopen(distantfile)
            with open(localfile, 'wb') as f:
                f.write(dist.read())

    tdt_folder = str(local_folder / 'tdt' / 'aep_05')
    return tdt_folder

def get_blackrock_files():
    url_for_tests = "https://web.gin.g-node.org/NeuralEnsemble/ephy_testing_data/raw/master/"

    files_to_download = [
        'blackrock/FileSpec2.3001.ns5',
        'blackrock/FileSpec2.3001.nev',
    ]

    local_folder = Path.home() / 'ephy_testing_data_http'

    for file in files_to_download:
        localfile = local_folder / file
        distantfile = url_for_tests + file
        if not localfile.is_file():
            localfile.parent.mkdir(exist_ok=True, parents=True)
            dist = urlopen(distantfile)
            with open(localfile, 'wb') as f:
                f.write(dist.read())

    filename = str(local_folder / 'blackrock' / 'FileSpec2.3001')
    return filename
