# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import ViewerBase, Base_ParamController
from .datasource import FrameGrabber, MultiVideoFileSource

default_params = [
    {'name': 'nb_column', 'type': 'int', 'value': 4},
    ]

default_by_channel_params = [ 
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]




class QFrameGrabber(QT.QObject, FrameGrabber):
    #~ frame_ready = QT.pyqtSignal(object, object)
    #~ update_frame_range = QtCore.pyqtSignal(object)
    frame_ready = QT.pyqtSignal(int, object)
    
    
    def on_request_frame(self, video_index, target_frame):
        
        
        if self.video_index!=video_index:
            return
        #~ print('on_request_frame', video_index, target_frame)
        
        frame = self.get_frame(target_frame)
        if not frame:
            return
        self.frame_ready.emit(self.video_index, frame)
        
        #~ rgba = frame.reformat(frame.width, frame.height, "rgb24", 'itu709')
        #print rgba.to_image().save("test.png")
        # could use the buffer interface here instead, some versions of PyQt don't support it for some reason
        # need to track down which version they added support for it
        #~ self.frame = bytearray(rgba.planes[0])
        #~ bytesPerPixel  =3 
        #~ img = QtGui.QImage(self.frame, rgba.width, rgba.height, rgba.width * bytesPerPixel, QtGui.QImage.Format_RGB888)
        
        #img = QtGui.QImage(rgba.planes[0], rgba.width, rgba.height, QtGui.QImage.Format_RGB888)

        #pixmap = QtGui.QPixmap.fromImage(img)
        #~ self.frame_ready.emit(img, target_frame)




class VideoViewer_ParamController(Base_ParamController):
    def __init__(self, parent=None, viewer=None):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)

    @property
    def visible_channels(self):
        visible = [self.viewer.by_channel_params.children()[i]['visible'] for i in range(self.source.nb_channel)]
        return np.array(visible, dtype='bool')



class VideoViewer(ViewerBase):

    _default_params = default_params
    _default_by_channel_params = default_by_channel_params
    
    _ControllerClass = VideoViewer_ParamController
    
    request_frame = QT.pyqtSignal(int, int)
    
    def __init__(self, with_user_dialog=True, **kargs):
        ViewerBase.__init__(self, **kargs)
        
        self.with_user_dialog = with_user_dialog
        
        self.make_params()
        
        if self.with_user_dialog and self._ControllerClass:
            self.params_controller = self._ControllerClass(parent=self, viewer=self)
            self.params_controller.setWindowFlags(QT.Qt.Window)
            #~ self.viewBox.doubleclicked.connect(self.show_params_controller)
        else:
            self.params_controller = None
        
        self.set_layout()
        
        self.frame_grabbers = []
        self.threads = []
        #~ self.actual_frames = []
        for i, video_filename in enumerate(self.source.video_filenames):
            fg = QFrameGrabber()
            self.frame_grabbers.append(fg)
            fg.set_file(video_filename)
            fg.video_index = i
            fg.frame_ready.connect(self.update_frame)
            
            thread = QT.QThread(parent=self)
            fg.moveToThread(thread)
            thread.start()
            self.threads.append(thread)
            
            self.request_frame.connect(self.frame_grabbers[i].on_request_frame)

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

    def make_params(self):
        # Create parameters
        all = []
        for i in range(self.source.nb_channel):
            #TODO add name, hadrware index, id
            name = 'Channel{}'.format(i)
            all.append({'name': name, 'type': 'group', 'children': self._default_by_channel_params})
        self.by_channel_params = pg.parametertree.Parameter.create(name='AnalogSignals', type='group', children=all)
        self.params = pg.parametertree.Parameter.create(name='Global options',
                                                    type='group', children=self._default_params)
        self.all_params = pg.parametertree.Parameter.create(name='all param',
                                    type='group', children=[self.params, self.by_channel_params])
        self.all_params.sigTreeStateChanged.connect(self.on_param_change)

    def set_layout(self):
        # layout
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.graphiclayout = pg.GraphicsLayoutWidget()
        self.mainlayout.addWidget(self.graphiclayout)
        self.create_grid()

    
    def show_params_controller(self):
        self.params_controller.show()
    
    def on_param_change(self):
        self.create_grid()
        self.refresh()
    
    def create_grid(self):
        
        visible_channels = self.params_controller.visible_channels
        nb_visible =sum(visible_channels)
        
        self.graphiclayout.clear()
        self.plots = [None] * self.source.nb_channel
        self.images = [None] * self.source.nb_channel
        r,c = 0,0
        
        rowspan = self.params['nb_column']
        colspan = nb_visible//self.params['nb_column']
        self.graphiclayout.ci.currentRow = 0
        self.graphiclayout.ci.currentCol = 0        
        for i in range(self.source.nb_channel):
            if not visible_channels[i]: continue

            viewBox = pg.ViewBox()
            viewBox.setAspectLocked()
            plot = pg.PlotItem(viewBox=viewBox)
            plot.hideButtons()
            plot.showAxis('left', False)
            plot.showAxis('bottom', False)

            self.graphiclayout.ci.layout.addItem(plot, r, c)  # , rowspan, colspan)
            if r not in self.graphiclayout.ci.rows:
                self.graphiclayout.ci.rows[r] = {}
            self.graphiclayout.ci.rows[r][c] = plot
            self.graphiclayout.ci.items[plot] = [(r,c)]
            self.plots[i] = plot
            
            self.images[i] = image = pg.ImageItem()
            #~ image.setPxMode(True)
            plot.addItem(image)
            
            
            c+=1
            if c==self.params['nb_column']:
                c=0
                r+=1

    def refresh(self):
        visible_channels = self.params_controller.visible_channels
        
        #~ print()
        #~ print('refresh t=', self.t)
        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                frame_index = self.source.time_to_frame_index(c, self.t)
                #~ print( 'c', c, 'frame_index', frame_index)
                
                if self.frame_grabbers[c].active_frame != frame_index:
                    self.frame_grabbers[c].active_frame = frame_index
                    self.request_frame.emit(c, frame_index)
    
    def update_frame(self, video_index, frame):
        #~ print('update_frame', video_index, frame)
        
        #TODO : find better solution!!!! to avoid copy
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
    
