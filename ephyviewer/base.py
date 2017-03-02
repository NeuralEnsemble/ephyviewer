# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

from .myqt import QT
import pyqtgraph as pg
import numpy as np

import weakref




class ViewerBase(QT.QWidget):
    
    time_changed = QT.pyqtSignal(float)
    
    def __init__(self, name='', source=None, **kargs):
        QT.QWidget.__init__(self, **kargs)
        
        self.name = name
        self.source = source
        self.t = 0.
    
    def seek(self, t):
        self.t = t
        self.refresh()
        
    def refresh(self):
        #overwrite this one
        raise(NotImplementedError)
    
    def set_settings(self, value):
        pass
    
    def get_settings(self):
        return None



class MyViewBox(pg.ViewBox):
    doubleclicked = QT.pyqtSignal()
    ygain_zoom = QT.pyqtSignal(float)
    xsize_zoom = QT.pyqtSignal(float)
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.disableAutoRange()
    def mouseClickEvent(self, ev):
        ev.accept()
    def mouseDoubleClickEvent(self, ev):
        self.doubleclicked.emit()
        ev.accept()
    def wheelEvent(self, ev):
        if ev.modifiers() == QT.Qt.ControlModifier:
            z = 5. if ev.delta()>0 else 1/5.
        else:
            z = 1.1 if ev.delta()>0 else 1/1.1
        self.ygain_zoom.emit(z)
        ev.accept()
    def mouseDragEvent(self, ev):
        if ev.button()== QT.RightButton:
            self.xsize_zoom.emit((ev.pos()-ev.lastPos()).x())
        else:
            pass
        ev.accept()


class BaseMultiChannelViewer(ViewerBase):

    _default_params = None
    _default_by_channel_params = None
    _ControllerClass = None
    
    def __init__(self, with_user_dialog=True, **kargs):
        ViewerBase.__init__(self, **kargs)
        
        self.with_user_dialog = with_user_dialog
        
        #~ self.make_params()
        #~ self.set_layout()
        #~ self.make_param_controller()

    def make_params(self):
        # Create parameters
        all = []
        for i in range(self.source.nb_channel):
            #TODO add name, hadrware index, id
            name = 'ch{}'.format(i)
            children =[{'name': 'name', 'type': 'str', 'value': self.source.get_channel_name(i), 'readonly':True}]
            children += self._default_by_channel_params
            all.append({'name': name, 'type': 'group', 'children': children})
        self.by_channel_params = pg.parametertree.Parameter.create(name='Channels', type='group', children=all)
        self.params = pg.parametertree.Parameter.create(name='Global options',
                                                    type='group', children=self._default_params)
        self.all_params = pg.parametertree.Parameter.create(name='all param',
                                    type='group', children=[self.params, self.by_channel_params])
        self.all_params.sigTreeStateChanged.connect(self.on_param_change)        
    
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
 
    def make_param_controller(self):
        if self.with_user_dialog and self._ControllerClass:
            self.params_controller = self._ControllerClass(parent=self, viewer=self)
            self.params_controller.setWindowFlags(QT.Qt.Window)
            self.params_controller.some_channel_changed.connect(self.on_param_change)
        else:
            self.params_controller = None

    def show_params_controller(self):
        self.params_controller.show()
    
    def on_param_change(self):
        self.refresh()
    
    def set_xsize(self, xsize):
        #~ print(self.__class__.__name__, 'set_xsize', xsize)
        self.params['xsize'] = xsize

    def set_settings(self, value):
        self.all_params.restoreState(value)
    
    def get_settings(self):
        return self.all_params.saveState()



class Base_ParamController(QT.QWidget):
    def __init__(self, parent=None, viewer=None):
        QT.QWidget.__init__(self, parent)
        
        # this controller is an attribute of the viewer
        # so weakref to avoid loop reference and Qt crash
        self._viewer = weakref.ref(viewer)
        
        # layout
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)
        t = 'Options for {}'.format(self.viewer.name)
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QT.QLabel('<b>'+t+'<\b>'))
        

    @property
    def viewer(self):
        return self._viewer()
    
    @property
    def source(self):
        return self._viewer().source



class Base_MultiChannel_ParamController(Base_ParamController):
    some_channel_changed = QT.pyqtSignal()
    
    def __init__(self, parent=None, viewer=None):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)


        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.v1 = QT.QVBoxLayout()
        h.addLayout(self.v1)
        self.tree_params = pg.parametertree.ParameterTree()
        self.tree_params.setParameters(self.viewer.params, showTop=True)
        self.tree_params.header().hide()
        self.v1.addWidget(self.tree_params)

        self.tree_by_channel_params = pg.parametertree.ParameterTree()
        self.tree_by_channel_params.header().hide()
        h.addWidget(self.tree_by_channel_params)
        self.tree_by_channel_params.setParameters(self.viewer.by_channel_params, showTop=True)        
        v = QT.QVBoxLayout()
        h.addLayout(v)
        
        
        if self.source.nb_channel>1:
            v.addWidget(QT.QLabel('<b>Select channel...</b>'))
            names = [p.name() + ': '+p['name'] for p in self.viewer.by_channel_params]
            self.qlist = QT.QListWidget()
            v.addWidget(self.qlist, 2)
            self.qlist.addItems(names)
            self.qlist.setSelectionMode(QT.QAbstractItemView.ExtendedSelection)
            
            for i in range(len(names)):
                self.qlist.item(i).setSelected(True)            
            v.addWidget(QT.QLabel('<b>and apply...<\b>'))
            
        
        
        but = QT.QPushButton('set visble')
        v.addWidget(but)
        but.clicked.connect(self.on_set_visible)

    @property
    def selected(self):
        selected = np.ones(self.viewer.source.nb_channel, dtype=bool)
        if self.viewer.source.nb_channel>1:
            selected[:] = False
            selected[[ind.row() for ind in self.qlist.selectedIndexes()]] = True
        return selected

    
    @property
    def visible_channels(self):
        visible = [self.viewer.by_channel_params['ch{}'.format(i), 'visible'] for i in range(self.source.nb_channel)]
        return np.array(visible, dtype='bool')

    def on_set_visible(self):
        # apply
        self.viewer.by_channel_params.blockSignals(True)
        #~ self.all_params.sigTreeStateChanged.connect(self.on_param_change)   
        
        visibles = self.selected
        for i,param in enumerate(self.viewer.by_channel_params.children()):
            param['visible'] = visibles[i]
        
        self.viewer.by_channel_params.blockSignals(False)
        self.some_channel_changed.emit()

