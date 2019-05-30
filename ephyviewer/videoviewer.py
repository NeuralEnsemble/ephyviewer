# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg
from pyqtgraph.util.mutex import Mutex

from .base import ViewerBase, BaseMultiChannelViewer,  Base_MultiChannel_ParamController
from .datasource import FrameGrabber, MultiVideoFileSource
from .tools import create_plot_grid

import threading

default_params = [
    {'name': 'nb_column', 'type': 'int', 'value': 4},
    ]

default_by_channel_params = [
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]




#~ class QFrameGrabber(QT.QObject, FrameGrabber):
    #~ frame_ready = QT.pyqtSignal(int, object)
    #~ def on_request_frame(self, video_index, target_frame):
        #~ if self.video_index!=video_index:
            #~ return
        #~ frame = self.get_frame(target_frame)
        #~ if not frame:
            #~ return
        #~ self.frame_ready.emit(self.video_index, frame)


class QFrameGrabber(QT.QObject):
    frame_ready = QT.pyqtSignal(int, object)

    def __init__(self, frame_grabber, video_index, parent=None):
        QT.QObject.__init__(self, parent)

        self.fg = frame_grabber
        self.video_index = video_index

        self.mutex = Mutex()
        self.request_list = []
        self._last_frame = None

    #~ def on_request_frame(self, video_index, target_frame):
        #~ if self.video_index!=video_index:
            #~ return
        #~ frame = self.fg.get_frame(target_frame)
        #~ if frame is None:
            #~ return
        #~ self.frame_ready.emit(self.video_index, frame)

    @property
    def last_frame(self):
        with self.mutex:
            return self._last_frame

    #~ @property
    #~ def active_frame(self):
        #~ return self.fg.active_frame

    #~ @active_frame.setter
    #~ def active_frame(self, value):
        #~ self.fg.active_frame = value

    #~ def queue_request_frame(self, target_frame):
        #~ print('queue_request_frame', threading.get_ident())
        #~ with self.mutex:
            #~ self.request_list.append(target_frame)
            #~ if len(self.request_list)>1:
                #~ self.request_frame.emit()

    def on_request_frame(self, video_index):
        if self.video_index!=video_index:
            return

        #~ print('on_request_frame', threading.get_ident())

        with self.mutex:
            #~ print('len(self.request_list)', len(self.request_list))
            if len(self.request_list)==0:
                return
            target_frame = self.request_list[-1]
            self.request_list = []

            if target_frame == self._last_frame:
                return

        frame = self.fg.get_frame(target_frame)
        with self.mutex:
            self._last_frame = target_frame
            #~ print('new self._last_frame', self._last_frame)
        #~ self.fg.active_frame = target_frame
        self.frame_ready.emit(self.video_index, frame)




class VideoViewer_ParamController(Base_MultiChannel_ParamController):
    pass

#~ class VideoViewer(ViewerBase):
class VideoViewer(BaseMultiChannelViewer):

    _default_params = default_params
    _default_by_channel_params = default_by_channel_params

    _ControllerClass = VideoViewer_ParamController

    request_frame = QT.pyqtSignal(int)

    def __init__(self, **kargs):
        BaseMultiChannelViewer.__init__(self, **kargs)

        self.make_params()
        self.make_param_controller()
        self.set_layout()

        self.qframe_grabbers = []
        self.threads = []
        #~ self.actual_frames = []
        for i, video_filename in enumerate(self.source.video_filenames):
            fg = QFrameGrabber(self.source.frame_grabbers[i], i)
            self.qframe_grabbers.append(fg)
            #~ fg.set_file(video_filename)
            #~ fg.video_index = i
            fg.frame_ready.connect(self.update_frame)

            thread = QT.QThread(parent=self)
            fg.moveToThread(thread)
            thread.start()
            self.threads.append(thread)

            self.request_frame.connect(self.qframe_grabbers[i].on_request_frame)

    @classmethod
    def from_filenames(cls, video_filenames, video_times, name):
        source = MultiVideoFileSource(video_filenames, video_times=video_times)
        view = cls(source=source, name=name)
        return view


    def closeEvent(self, event):
        for i, thread in enumerate(self.threads):
            thread.quit()
            thread.wait()
        event.accept()


    def set_layout(self):
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.graphiclayout = pg.GraphicsLayoutWidget()
        self.mainlayout.addWidget(self.graphiclayout)
        self.create_grid()

    def on_param_change(self):
        self.create_grid()
        self.refresh()

    def create_grid(self):
        visible_channels = self.params_controller.visible_channels
        self.plots = create_plot_grid(self.graphiclayout, self.params['nb_column'], visible_channels,
                     ViewBoxClass=pg.ViewBox, vb_params={'lockAspect':True})

        for plot in self.plots:
            plot.showAxis('left', False)
            plot.showAxis('bottom', False)


        self.images = []
        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                image = pg.ImageItem()
                self.plots[c].addItem(image)
                self.images.append(image)
            else:
                self.images.append(None)

    def refresh(self):
        #~ print('videoviewer.refresh', self.t)
        visible_channels = self.params_controller.visible_channels

        #~ print()
        #~ print('refresh t=', self.t)
        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                frame_index = self.source.time_to_frame_index(c, self.t)
                #~ print( 'c', c, 'frame_index', frame_index, 'self.qframe_grabbers[c].last_frame', self.qframe_grabbers[c].last_frame)

                #~ if self.qframe_grabbers[c].active_frame != frame_index:
                #~ print('self.qframe_grabbers[c].last_frame != frame_index', self.qframe_grabbers[c].last_frame != frame_index)
                if self.qframe_grabbers[c].last_frame != frame_index:

                    #~ self.qframe_grabbers[c].active_frame = frame_index
                    #~ self.request_frame.emit(c, frame_index)

                    #~ self.qframe_grabbers[c].queue_request_frame(frame_index)
                    #~ print('enque frame', threading.get_ident(), 'frame_index', frame_index)
                    with self.qframe_grabbers[c].mutex:

                        self.qframe_grabbers[c].request_list.append(frame_index)
                        if len(self.qframe_grabbers[c].request_list)>=1:
                            self.request_frame.emit(c)
                            #~ print('EMIT!!!!!')







    def update_frame(self, video_index, frame):
        #~ print('update_frame', video_index, frame)

        if frame is None:
            self.images[video_index].clear()
        else:
            #TODO : find better solution!!!! to avoid copy
            try:
                # PyAV >= 0.5.3
                img = frame.to_ndarray(format='rgb24')
            except AttributeError:
                # PyAV < 0.5.3
                img = frame.to_nd_array(format='rgb24')
            img = img.swapaxes(0,1)[:,::-1,:]
            #~ print(img.shape, img.dtype)
            self.images[video_index].setImage(img)


        #~ rgba = frame.reformat(frame.width, frame.height, "rgb24", 'itu709')
        #print rgba.to_image().save("test.png")
        # could use the buffer interface here instead, some versions of PyQt don't support it for some reason
        # need to track down which version they added support for it
        #~ bytearray(rgba.planes[0])
        #~ bytesPerPixel  =3
        #~ img = QT.QImage(bytearray(rgba.planes[0]), rgba.width, rgba.height, rgba.width * bytesPerPixel, QT.QImage.Format_RGB888)
        #~ self.images[video_index].setImage(img)

        #img = QtGui.QImage(rgba.planes[0], rgba.width, rgba.height, QtGui.QImage.Format_RGB888)







                #~ if self.actual_frames[i] != new_frame:





                #~ frame = self.source.get_frame(t=t,chan=c)
                #~ self.images[c].setImage(frame)
            #~ else:
                #~ pass
