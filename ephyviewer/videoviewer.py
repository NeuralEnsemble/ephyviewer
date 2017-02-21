# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)


import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
import pyqtgraph as pg

from .base import ViewerBase, Base_ParamController

default_params = [
    {'name': 'nb_column', 'type': 'int', 'value': 4},
    ]

default_by_channel_params = [ 
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]


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
    
    def __init__(self, with_user_dialog=True, **kargs):
        ViewerBase.__init__(self, **kargs)
        
        self.with_user_dialog = with_user_dialog
        
        self.make_params()
        self.set_layout()

        if self.with_user_dialog and self._ControllerClass:
            self.params_controller = self._ControllerClass(parent=self, viewer=self)
            self.params_controller.setWindowFlags(QT.Qt.Window)
            #~ self.viewBox.doubleclicked.connect(self.show_params_controller)
        else:
            self.params_controller = None

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
        for i in range(self.nb_channel):
            if not visible_channels[i]: continue

            viewBox = MyViewBox()
            if self.with_user_dialog:
                viewBox.doubleclicked.connect(self.show_params_controller)
            #~ viewBox.gain_zoom.connect(self.clim_zoom)
            #~ viewBox.xsize_zoom.connect(self.xsize_zoom)
            
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
            c+=1
            if c==self.params['nb_column']:
                c=0
                r+=1

    def refresh(self):
        visible_channels = self.params_controller.visible_channels
        
        for c in range(self.source.nb_channel):
            if visible_channels[c]:
                frame = self.source.get_frame(t=t,chan=c)
                self.images[c].setImage(frame)
            else:
                pass

