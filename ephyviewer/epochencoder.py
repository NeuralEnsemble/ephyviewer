# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from collections import OrderedDict
import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
from . import tools

import pyqtgraph as pg

from .base import ViewerBase, Base_ParamController, MyViewBox
from .epochviewer import RectItem, DataGrabber


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1, 'limits':(0,np.inf)},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'new_epoch_step', 'type': 'float', 'value': .1, 'step': 0.1, 'limits':(0,np.inf)},
    {'name': 'view_mode', 'type': 'list', 'value':'stacked', 'values' : ['stacked', 'flat']},
    
    #~ {'name': 'display_labels', 'type': 'bool', 'value': True},
    ]



class EpochEncoder_ParamController(Base_ParamController):
    def __init__(self, parent=None, viewer=None, with_visible=True, with_color=True):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)

        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.v1 = QT.QVBoxLayout()
        h.addLayout(self.v1)
        self.tree_label_params = pg.parametertree.ParameterTree()
        self.tree_label_params.setParameters(self.viewer.by_label_params, showTop=True)
        self.tree_label_params.header().hide()
        self.v1.addWidget(self.tree_label_params)

        #~ self.v1 = QT.QVBoxLayout()
        #~ h.addLayout(self.v1)
        #~ self.tree_params = pg.parametertree.ParameterTree()
        #~ self.tree_params.setParameters(self.viewer.params, showTop=True)
        #~ self.tree_params.header().hide()
        #~ self.v1.addWidget(self.tree_params)



class EpochEncoder(ViewerBase):
    _default_params = default_params
    
    request_data = QT.pyqtSignal(float, float, object)
    
    def __init__(self, **kargs):
        ViewerBase.__init__(self, **kargs)
        
        self.make_params()
        self.set_layout()
        self.make_param_controller()
        
        self.viewBox.doubleclicked.connect(self.show_params_controller)
        
        self.initialize_plot()
        
        self._xratio = 0.3
        
        self.thread = QT.QThread(parent=self)
        self.datagrabber = DataGrabber(source=self.source)
        self.datagrabber.moveToThread(self.thread)
        self.thread.start()
        
        
        self.datagrabber.data_ready.connect(self.on_data_ready)
        self.request_data.connect(self.datagrabber.on_request_data)

    def make_params(self):
        # Create parameters
        self.params = pg.parametertree.Parameter.create(name='Global options',
                                                    type='group', children=self._default_params)
        self.params.sigTreeStateChanged.connect(self.on_param_change)
        
        
        keys = 'azertyuiop'
        all = []
        self.shortcuts = OrderedDict()
        for i, label in enumerate(self.source.possible_labels):
            key = keys[i] if i<len(keys) else ''
            
            name = 'label{}'.format(i)
            children =[{'name': 'name', 'type': 'str', 'value': self.source.possible_labels[i], 'readonly':True},
                            {'name': 'color', 'type': 'color', 'value': self.source.color_by_label(label)},
                            {'name': 'key', 'type': 'str', 'value': key},
                            ]
            all.append({'name': name, 'type': 'group', 'children': children})
            shortcut = QT.QShortcut (self)
            if key != '':
                shortcut.setKey(key)
            shortcut.activated.connect(self.on_shortcut)
            self.shortcuts[shortcut] = label
            
        self.by_label_params = pg.parametertree.Parameter.create(name='Labels', type='group', children=all)
        self.by_label_params.sigTreeStateChanged.connect(self.on_change_keys)
    
    
    def set_layout(self):
        # layout
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.viewBox = MyViewBox()
        
        self.graphicsview  = pg.GraphicsView()#useOpenGL = True)
        self.mainlayout.addWidget(self.graphicsview)
        
        self.plot = pg.PlotItem(viewBox=self.viewBox)
        self.plot.hideButtons()
        self.graphicsview.setCentralItem(self.plot)
        
        self.mainlayout.addSpacing(10)
        
        #~ g = QT.QGridLayout()
        #~ self.mainlayout.addLayout(g)
        
        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)
        v = QT.QVBoxLayout()
        h.addLayout(v)
        
        but = QT.PushButton('Colors and keys')
        v.addWidget(but)
        but.clicked.connect(self.show_params_controller)
        
        but = QT.PushButton('Merge neighbors')
        v.addWidget(but)
        but.clicked.connect(self.on_merge_neighbors)

        but = QT.PushButton('Fill blank')
        v.addWidget(but)
        but.clicked.connect(self.on_fill_blank)
        
        
        v.addStretch()

        but = QT.PushButton('Save')
        v.addWidget(but)
        but.clicked.connect(self.on_save)
        
        
        #~ g.addWidget(QT.QLabel('Step on key'), 1, 0)
        #~ self.spin_step = pg.SpinBox(value=.1, decimals = 8, bounds = (-np.inf, np.inf),step = 0.05, siPrefix=False, suffix='s', int=False)
        #~ g.addWidget(self.spin_step, 1, 1)

        self.tree_params = pg.parametertree.ParameterTree()
        self.tree_params.setParameters(self.params, showTop=True)
        self.tree_params.header().hide()
        h.addWidget(self.tree_params)        

 
    def make_param_controller(self):
        self.params_controller = EpochEncoder_ParamController(parent=self, viewer=self)
        self.params_controller.setWindowFlags(QT.Qt.Window)


    def closeEvent(self, event):
        event.accept()
        self.thread.quit()
        self.thread.wait()

    
    def initialize_plot(self):
        pass

    def show_params_controller(self):
        self.params_controller.show()
    
    def on_param_change(self):
        self.refresh()
    
    def on_change_keys(self):
        
        for i, label in enumerate(self.source.possible_labels):
            key = self.by_label_params['label'+str(i), 'key']
            shortcut = list(self.shortcuts.keys())[i]
            print(shortcut)
            shortcut.setKey(key)
        
        self.refresh()
    
    def set_xsize(self, xsize):
        self.params['xsize'] = xsize

    def set_settings(self, value):
        pass
    
    def get_settings(self):
        pass
        #~ return self.all_params.saveState()
    
    def refresh(self):
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        self.request_data.emit(t_start, t_stop, [0])

    def on_data_ready(self, t_start, t_stop, visibles, data):
        #~ print('on_data_ready', self, t_start, t_stop, visibles, data)
        self.plot.clear()
        self.graphicsview.setBackground(self.params['background_color'])
        
        times, durations, labels = data[0]
        
        n = len(self.source.possible_labels)
        
        for i, label in enumerate(labels):
            ind = self.source.possible_labels.index(label)
            color = self.by_label_params['label'+str(ind), 'color']
            ypos = n - ind - 1
            if self.params['view_mode']=='stacked':
                ypos = n - ind - 1
            else:
                ypos = 0
            item = RectItem([times[i],  ypos,durations[i], .9],  border=color, fill=color)
            item = RectItem([times[i],  ypos,durations[i], .9],  border='#FFFFFF', fill=color)
            item.setPos(times[i],  ypos)
            self.plot.addItem(item)
        
        if self.params['view_mode']=='stacked':
            for i, label in enumerate(self.source.possible_labels):
                color = self.by_label_params['label'+str(i), 'color']
                label_item = pg.TextItem(label, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 120)))
                self.plot.addItem(label_item)
                label_item.setPos(t_start, n - i - 0.55)

        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = '#00FF00')
        self.plot.addItem(self.vline)

        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        if self.params['view_mode']=='stacked':
            self.plot.setYRange( 0, n)
        else:
            self.plot.setYRange( 0, 1)
    
    def on_shortcut(self):
        label = self.shortcuts.get(self.sender(), None)
        if label is None: return
        
        #~ duration = self.spin_step.value()
        duration = self.params['new_epoch_step']
        
        self.source.add_epoch(self.t, duration, label)
        
        self.t += duration
        self.refresh()
        self.time_changed.emit(self.t)
    
    def on_merge_neighbors(self):
        self.source.merge_neighbors()
        self.refresh()
    
    def on_fill_blank(self):
        params = [{'name': 'method', 'type': 'list', 'value':'from_left', 'values' : ['from_left', 'from_right', 'from_nearest']}]
        dia = tools.ParamDialog(params, title='Fill blank method', parent=self)
        dia.resize(300, 100)
        if dia.exec_():
            d = dia.get()
            method = d['method']
            self.source.fill_blank(method=method)
            self.refresh()
    
    def on_save(self):
        self.source.save()


