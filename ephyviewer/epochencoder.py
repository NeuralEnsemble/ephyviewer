# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from collections import OrderedDict
import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
from . import tools

import pyqtgraph as pg

from .base import ViewerBase, Base_ParamController, MyViewBox, same_param_tree
from .epochviewer import RectItem, DataGrabber


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'new_epoch_step', 'type': 'float', 'value': .1, 'step': 0.1, 'limits':(0,np.inf)},
    {'name': 'view_mode', 'type': 'list', 'value':'stacked', 'values' : ['stacked', 'flat']},
    
    #~ {'name': 'display_labels', 'type': 'bool', 'value': True},
    ]



class EpochEncoder_ParamController(Base_ParamController):
    def __init__(self, parent=None, viewer=None, with_visible=True, with_color=True):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)
        
        self.resize(400, 600)

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
        
        self._xratio = 0.3
        
        self.initialize_plot()
        
        self.on_range_visibility_changed(None, refresh=False)
        
        
        
        self.thread = QT.QThread(parent=self)
        self.datagrabber = DataGrabber(source=self.source)
        self.datagrabber.moveToThread(self.thread)
        self.thread.start()
        
        
        self.datagrabber.data_ready.connect(self.on_data_ready)
        self.request_data.connect(self.datagrabber.on_request_data)
        
        self.refresh_table()
        

    def make_params(self):
        # Create parameters
        self.params = pg.parametertree.Parameter.create(name='Global options',
                                                    type='group', children=self._default_params)
        self.params.param('xsize').setLimits((0, np.inf))
        
        
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
        
        
        self.all_params = pg.parametertree.Parameter.create(name='all param',
                                    type='group', children=[self.params, self.by_label_params])
        
        self.params.sigTreeStateChanged.connect(self.on_param_change)
        self.by_label_params.sigTreeStateChanged.connect(self.on_change_keys)
    
    
    def set_layout(self):
        # layout
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.viewBox = MyViewBox()
        
        self.graphicsview  = pg.GraphicsView()#useOpenGL = True)
        self.mainlayout.addWidget(self.graphicsview, 4)
        
        self.plot = pg.PlotItem(viewBox=self.viewBox)
        self.plot.hideButtons()
        self.graphicsview.setCentralItem(self.plot)
        
        self.mainlayout.addSpacing(10)
        
        
        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        g = QT.QGridLayout()
        h.addLayout(g)

        but = QT.PushButton('Colors and keys')
        g.addWidget(but, 0, 0)
        
        but.clicked.connect(self.show_params_controller)
        
        but = QT.PushButton('Merge neighbors')
        g.addWidget(but, 1, 0)
        but.clicked.connect(self.on_merge_neighbors)

        but = QT.PushButton('Fill blank')
        g.addWidget(but, 2, 0)
        but.clicked.connect(self.on_fill_blank)

        but = QT.PushButton('Save')
        g.addWidget(but, 4, 0)
        but.clicked.connect(self.on_save)
        
        
        #~ v.addStretch()
        #~ v.addWidget(QT.QFrame(frameShape=QT.QFrame.HLine, frameShadow=QT.QFrame.Sunken))
        
        self.but_range = QT.PushButton('Show/hide range', checkable=True)
        g.addWidget(self.but_range, 0, 1)
        self.but_range.clicked.connect(self.on_range_visibility_changed)
        
        spinboxs = []
        buts = []
        for i in range(2):
            hh = QT.QHBoxLayout()
            g.addLayout(hh, 1+i, 1)
            but = QT.QPushButton('>')
            buts.append(but)
            hh.addWidget(but)
            spinbox = pg.SpinBox(value=float(i), decimals = 8, bounds = (-np.inf, np.inf),step = 0.05, siPrefix=False, int=False)
            hh.addWidget(spinbox, 10)
            #~ g.addWidget(spinbox, 1+i, 1)
            spinbox.setSizePolicy(QT.QSizePolicy.Preferred, QT.QSizePolicy.Preferred, )
            spinbox.valueChanged.connect(self.on_spin_limit_changed)
            spinboxs.append(spinbox)
        self.spin_limit1, self.spin_limit2 = spinboxs
        buts[0].clicked.connect(self.set_limit1)
        buts[1].clicked.connect(self.set_limit2)
        
        
        self.combo_labels = QT.QComboBox()
        self.combo_labels.addItems(self.source.possible_labels)
        g.addWidget(self.combo_labels, 3, 1)
        
        self.but_apply_region = QT.PushButton('Apply')
        g.addWidget(self.but_apply_region, 4, 1)
        self.but_apply_region.clicked.connect(self.apply_region)

        self.but_del_region = QT.PushButton('Delete')
        g.addWidget(self.but_del_region, 5, 1)
        self.but_del_region.clicked.connect(self.delete_region)
        
        
        self.tree_params = pg.parametertree.ParameterTree()
        self.tree_params.setParameters(self.params, showTop=True)
        self.tree_params.header().hide()
        h.addWidget(self.tree_params)
        
        self.table_widget = QT.QTableWidget()
        h.addWidget(self.table_widget)
        self.table_widget.itemSelectionChanged.connect(self.on_seek_table)
        self.table_widget.setSelectionMode(QT.QAbstractItemView.SingleSelection)
        self.table_widget.setSelectionBehavior(QT.QAbstractItemView.SelectRows)
        

 
    def make_param_controller(self):
        self.params_controller = EpochEncoder_ParamController(parent=self, viewer=self)
        self.params_controller.setWindowFlags(QT.Qt.Window)


    def closeEvent(self, event):
        
        text = 'save ?'
        title = 'quit'
        mb = QT.QMessageBox.question(self, title,text, 
                QT.QMessageBox.Ok ,  QT.QMessageBox.Discard)
        if mb==QT.QMessageBox.Ok:
            self.source.save()
        
        self.thread.quit()
        self.thread.wait()
        event.accept()

    
    def initialize_plot(self):
        self.region = pg.LinearRegionItem(brush='#FF00FF20')
        self.region.setZValue(10)
        self.region.setRegion((0, 1.))
        self.plot.addItem(self.region, ignoreBounds=True)
        self.region.sigRegionChanged.connect(self.on_region_changed)

        self.vline = pg.InfiniteLine(angle=90, movable=False, pen='#00FF00')
        self.plot.addItem(self.vline)
        
        self.rect_items = []
        
        self.label_items = []
        for i, label in enumerate(self.source.possible_labels):
            color = self.by_label_params['label'+str(i), 'color']
            label_item = pg.TextItem(label, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 120)))
            self.plot.addItem(label_item)
            self.label_items.append(label_item)

        

    def show_params_controller(self):
        self.params_controller.show()
    
    def on_param_change(self):
        self.refresh()
    
    def on_change_keys(self, refresh=True):
        
        for i, label in enumerate(self.source.possible_labels):
            key = self.by_label_params['label'+str(i), 'key']
            shortcut = list(self.shortcuts.keys())[i]
            #~ print(shortcut)
            shortcut.setKey(key)
        
        self.refresh()
    
    def set_xsize(self, xsize):
        self.params['xsize'] = xsize


    def set_settings(self, value):
        #~ print('set_settings')
        actual_value = self.all_params.saveState()
        #~ print('same tree', same_param_tree(actual_value, value))
        if same_param_tree(actual_value, value):
            # this prevent restore something that is not same tree
            # as actual. Possible when new features.
            self.params.blockSignals(True)
            self.by_label_params.blockSignals(True)
            
            self.all_params.restoreState(value)
            
            self.params.blockSignals(False)
            self.by_label_params.blockSignals(False)
            self.on_change_keys(refresh=False)
        else:
            print('Not possible to restore setiings')
    
    def get_settings(self):
        return self.all_params.saveState()

    def refresh(self):
        xsize = self.params['xsize']
        t_start, t_stop = self.t-xsize*self._xratio , self.t+xsize*(1-self._xratio)
        self.request_data.emit(t_start, t_stop, [0])

    def on_data_ready(self, t_start, t_stop, visibles, data):
        #~ print('on_data_ready', self, t_start, t_stop, visibles, data)
        #~ self.plot.clear()
        
        for rect_item in self.rect_items:
            self.plot.removeItem(rect_item)
        self.rect_items = []
        
        self.graphicsview.setBackground(self.params['background_color'])
        
        times, durations, labels = data[0]
        #~ print(data)
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
            self.rect_items.append(item)
        
        
        #~ for i, label in enumerate(self.source.possible_labels):
        for i, label_item in enumerate(self.label_items):
            if self.params['view_mode']=='stacked':
                color = self.by_label_params['label'+str(i), 'color']
                #~ label_item = pg.TextItem(label, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 120)))
                label_item.setColor(color)
                label_item.setPos(t_start, n - i - 0.55)
                label_item.show()
                #~ self.plot.addItem(label_item)
            else:
                label_item.hide()
        
        if self.but_range.isChecked():
            self.region.show()
        else:
            self.region.hide()
        
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
        self.refresh_table()
    
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
            self.refresh_table()
    
    
    def on_save(self):
        self.source.save()
    
    def on_spin_limit_changed(self, v):
        self.region.blockSignals(True)
        rgn = (self.spin_limit1.value(), self.spin_limit2.value())
        rgn = self.region.setRegion(rgn)
        self.region.blockSignals(False)
    
    def on_region_changed(self):
        self.spin_limit1.blockSignals(True)
        self.spin_limit2.blockSignals(True)
        rgn = self.region.getRegion()
        self.spin_limit1.setValue(rgn[0])
        self.spin_limit2.setValue(rgn[1])
        self.spin_limit1.blockSignals(False)
        self.spin_limit2.blockSignals(False)

    def apply_region(self):
        rgn = self.region.getRegion()
        t = rgn[0]
        duration = rgn[1] - rgn[0]
        label = str(self.combo_labels.currentText())
        self.source.add_epoch(t, duration, label)
        
        self.refresh()
        self.refresh_table()
    
    def delete_region(self):
        rgn = self.region.getRegion()
        
        self.source.delete_in_between(rgn[0], rgn[1])
        
        self.refresh()
        self.refresh_table()
        
    
    def on_range_visibility_changed(self, flag, refresh=True):
        enabled = self.but_range.isChecked()
        #~ print(enabled)
        for w in (self.spin_limit1, self.spin_limit2, self.combo_labels, self.but_apply_region, self.but_del_region):
            w.setEnabled(enabled)
            
        if enabled:
            rgn = self.region.getRegion()
            rgn = (self.t, self.t + rgn[1] - rgn[0])
            self.region.setRegion(rgn)
        self.refresh()

    def set_limit1(self):
        if self.t<self.spin_limit2.value():
            self.spin_limit1.setValue(self.t)

    def set_limit2(self):
        if self.t>self.spin_limit1.value():
            self.spin_limit2.setValue(self.t)
    
    def refresh_table(self):
        self.table_widget.clear()
        #~ ev = self.source.all_events[ind]
        times, durations, labels = self.source.get_chunk(chan=0,  i_start=None, i_stop=None)
        self.table_widget.setColumnCount(4)
        self.table_widget.setRowCount(times.size)
        self.table_widget.setHorizontalHeaderLabels(['start', 'stop', 'duration', 'label'])
        for r in range(times.size):
            
            values = [times[r], times[r]+durations[r], durations[r], labels[r]]
            for c, value in enumerate(values):
                item = QT.QTableWidgetItem('{}'.format(value))
                item.setFlags(QT.ItemIsSelectable|QT.ItemIsEnabled)
                self.table_widget.setItem(r, c, item)
    
    def on_seek_table(self):
        if self.table_widget.rowCount()==0:
            return
        selected_ind = self.table_widget.selectedIndexes()
        if len(selected_ind)==0:
            return
        i = selected_ind[0].row()
        t, _, _= self.source.get_chunk(chan=0,  i_start=i, i_stop=i+1)
        self.t = t[0]
        self.refresh()
        self.time_changed.emit(self.t)
        
        


