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
        
        self.make_params()
        self.set_layout()

        if self.with_user_dialog and self._ControllerClass:
            self.params_controller = self._ControllerClass(parent=self, viewer=self)
            self.params_controller.setWindowFlags(QT.Qt.Window)
            self.viewBox.doubleclicked.connect(self.show_params_controller)
        else:
            self.params_controller = None

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