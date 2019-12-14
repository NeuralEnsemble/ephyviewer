# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from .sourcebase import BaseDataSource
import sys


import numpy as np

try:
    import av
    HAVE_AV = True
except ImportError:
    HAVE_AV = False


AV_TIME_BASE = 1000000

def pts_to_frame(pts, time_base, frame_rate, start_time):
    return int(pts * time_base * frame_rate) - int(start_time * time_base * frame_rate)

def get_frame_rate(stream):

    if stream.average_rate.denominator and stream.average_rate.numerator:
        return float(stream.average_rate)
    if stream.time_base.denominator and stream.time_base.numerator:
        return 1.0/float(stream.time_base)
    else:
        raise ValueError("Unable to determine FPS")

#~ def get_frame_count(f, stream):

    #~ if stream.frames:
        #~ return stream.frames
    #~ elif stream.duration:
        #~ return pts_to_frame(stream.duration, float(stream.time_base), get_frame_rate(stream), 0)
    #~ elif f.duration:
        #~ return pts_to_frame(f.duration, 1/float(AV_TIME_BASE), get_frame_rate(stream), 0)

    #~ else:
        #~ raise ValueError("Unable to determine number for frames")



class FrameGrabber:
    """

    this is taken from pyav example here but without QT stuff.
    https://github.com/mikeboers/PyAV/blob/master/scratchpad/frame_seek_example.py
    """

    def __init__(self):
        self.file = None
        self.stream = None
        self.frame = None

        self.start_time = 0
        self.pts_seen = False
        self.nb_frames = None

        self.rate = None
        self.time_base = None

        self.last_frame = None
        self.last_frame_index = None

    def next_frame(self):

        frame_index = None

        rate = self.rate
        time_base = self.time_base

        self.pts_seen = False

        for packet in self.file.demux(self.stream):
            #~ print("    pkt", packet.pts, packet.dts, packet)
            if packet.pts:
                self.pts_seen = True

            for frame in packet.decode():
                #~ print('   frame', frame)
                if frame_index is None:

                    if self.pts_seen:
                        pts = frame.pts
                    else:
                        pts = frame.dts
                    #~ print('  pts',pts)
                    if not pts is None:
                        frame_index = pts_to_frame(pts, time_base, rate, self.start_time)

                elif not frame_index is None:
                    frame_index += 1


                yield frame_index, frame

    def get_frame(self, target_frame):
        #~ print('get_frame', target_frame)

        if target_frame == self.last_frame_index:
            frame = self.last_frame
        elif target_frame < 0 or target_frame >= self.nb_frames:
            frame = None
        elif self.last_frame_index is None or \
                (target_frame < self.last_frame_index) or \
                (target_frame > self.last_frame_index + 300):
            frame = self.get_frame_absolut_seek(target_frame)
        else:
            frame = None
            for i, (frame_index, next_frame) in enumerate(self.next_frame()):
                #~ print("   ", i, "NEXT at frame", next_frame, "at ts:", next_frame.pts,next_frame.dts)
                if frame_index is None or frame_index >= target_frame:
                    frame = next_frame
                    break

        if frame is not None:
            self.last_frame = frame
            self.last_frame_index = target_frame

        return frame



    def get_frame_absolut_seek(self, target_frame):
        #~ print('get_frame_absolut_seek', target_frame)
        #~ print('self.active_frame', self.active_frame)

        #~ if target_frame != self.active_frame:
            #~ print('YEP')
            #~ return
        #~ print 'seeking to', target_frame

        seek_frame = target_frame

        rate = self.rate
        time_base = self.time_base
        #~ print 'ici', rate, time_base, 'target_frame', target_frame

        frame = None
        reseek = 250

        original_target_frame_pts = None

        while reseek >= 0:

            # convert seek_frame to pts
            target_sec = seek_frame * 1/rate
            target_pts = int(target_sec / time_base) + self.start_time

            #~ print 'la', 'target_sec', target_sec, 'target_pts', target_pts

            if original_target_frame_pts is None:
                original_target_frame_pts = target_pts

            try:
                # PyAV >= 6.1.0
                self.file.seek(int(target_pts), stream=self.stream)
            except TypeError:
                # PyAV < 6.1.0
                self.stream.seek(int(target_pts))

            frame_index = None

            frame_cache = []

            for i, (frame_index, frame) in enumerate(self.next_frame()):

                #~ # optimization if the time slider has changed, the requested frame no longer valid
                #~ if target_frame != self.active_frame:
                    #~ print('YEP0 target_frame != self.active_frame', target_frame, self.active_frame)
                    #~ return

                #~ print("   ", i, "at frame", frame_index, "at ts:", frame.pts,frame.dts,"target:", target_pts, 'orig', original_target_frame_pts)

                if frame_index is None:
                    pass

                elif frame_index >= target_frame:
                    break

                frame_cache.append(frame)

            # Check if we over seeked, if we over seekd we need to seek to a earlier time
            # but still looking for the target frame
            if frame_index != target_frame:

                if frame_index is None:
                    over_seek = '?'
                else:
                    over_seek = frame_index - target_frame
                    if frame_index > target_frame:

                        #~ print over_seek, frame_cache
                        if over_seek <= len(frame_cache):
                            #~ print "over seeked by %i, using cache" % over_seek
                            frame = frame_cache[-over_seek]
                            break


                seek_frame -= 1
                reseek -= 1
                #~ print "over seeked by %s, backtracking.. seeking: %i target: %i retry: %i" % (str(over_seek),  seek_frame, target_frame, reseek)

            else:
                break

        #~ print('ici frame', frame)
        if reseek < 0:
            #~ print('YEP reseek < 0')
            #~ raise ValueError("seeking failed %i" % frame_index)
            return None

        # frame at this point should be the correct frame

        if frame:

            return frame

        else:
            return None
            #~ raise ValueError("seeking failed %i" % target_frame)

    def get_frame_count(self):

        frame_count = None

        if self.stream.frames:
            frame_count = self.stream.frames
        elif self.stream.duration:
            frame_count =  pts_to_frame(self.stream.duration, float(self.stream.time_base), get_frame_rate(self.stream), 0)
        elif self.file.duration:
            frame_count = pts_to_frame(self.file.duration, 1/float(AV_TIME_BASE), get_frame_rate(self.stream), 0)
        else:
            raise ValueError("Unable to determine number for frames")

        seek_frame = frame_count

        retry = 100

        while retry:
            target_sec = seek_frame * 1/ self.rate
            target_pts = int(target_sec / self.time_base) + self.start_time

            try:
                # PyAV >= 6.1.0
                self.file.seek(int(target_pts), stream=self.stream)
            except TypeError:
                # PyAV < 6.1.0
                self.stream.seek(int(target_pts))

            frame_index = None

            for frame_index, frame in self.next_frame():
                #~ print frame_index, frame
                continue

            if not frame_index is None:
                break
            else:
                seek_frame -= 1
                retry -= 1


        #~ print "frame count seeked", frame_index, "container frame count", frame_count

        return frame_index or frame_count

    def set_file(self, path):
        #~ print(path, type(path))
        self.file = av.open(path)
        #~ for s in self.file.streams:
            #~ print(s.type)
        #~ self.stream = next(s for s in self.file.streams if s.type == b'video') #py2
        self.stream = next(s for s in self.file.streams if s.type == 'video')

        self.rate = get_frame_rate(self.stream)
        self.time_base = float(self.stream.time_base)


        index, first_frame = next(self.next_frame())

        try:
            # PyAV >= 6.1.0
            self.file.seek(self.stream.start_time or 0, stream=self.stream)
        except TypeError:
            # PyAV < 6.1.0
            self.stream.seek(self.stream.start_time or 0)

        # find the pts of the first frame
        index, first_frame = next(self.next_frame())

        if self.pts_seen:
            pts = first_frame.pts
        else:
            pts = first_frame.dts

        self.start_time = pts or first_frame.dts

        #~ print("First pts", pts, self.stream.start_time, first_frame)

        #self.nb_frames = get_frame_count(self.file, self.stream)
        self.nb_frames = self.get_frame_count()




class MultiVideoFileSource( BaseDataSource):
    type = 'video'
    def __init__(self, video_filenames, video_times=None):
        assert HAVE_AV, 'PyAv is not installed'

        self.video_filenames = video_filenames
        self.video_times = video_times
        n = len(self.video_filenames)

        self.t_starts, self.t_stops, self.rates = [], [], []
        self.nb_frames = []
        self.frame_grabbers = []
        for video_filename in self.video_filenames:
            fg = FrameGrabber()
            fg.set_file(video_filename)
            self.frame_grabbers.append(fg)

            self.nb_frames.append(fg.get_frame_count())
            self.rates.append(fg.rate)
            self.t_starts.append(fg.start_time)
            self.t_stops.append(fg.start_time+fg.stream.duration*fg.time_base)

        self._t_start = min(self.t_starts)
        self._t_stop = max(self.t_stops)

    @property
    def nb_channel(self):
        return len(self.video_filenames)

    def get_channel_name(self, chan=0):
        return 'video {}'.format(chan)

    @property
    def t_start(self):
        return self._t_start

    @property
    def t_stop(self):
        return self._t_stop

    def time_to_frame_index(self, i, t):

        # if t is between frames, both methods return
        # the index of the frame *preceding* t
        if self.video_times is None:
            frame_index = int((t-self.t_starts[i])*self.rates[i])
        else:
            frame_index = np.searchsorted(self.video_times[i], t, side='right') - 1

        return frame_index
