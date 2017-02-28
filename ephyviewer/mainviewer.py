# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

from collections import OrderedDict
import time
import sys
import pickle

from .myqt import QT
from .navigation import NavigationToolBar

location_to_qt={
    'left': QT.LeftDockWidgetArea,
    'right': QT.RightDockWidgetArea,
    'top': QT.TopDockWidgetArea,
    'bottom': QT.BottomDockWidgetArea,
}

orientation_to_qt={
    'horizontal': QT.Horizontal,
    'vertical': QT.Vertical,
}


class MainViewer(QT.QMainWindow):
    def __init__(self, debug=False, settings_name=None, **navigation_params):
        QT.QMainWindow.__init__(self)

        #TODO settings
        #http://www.programcreek.com/python/example/86789/PyQt5.QtCore.QSettings
        
        self.debug = debug
        self.settings_name = settings_name
        if self.settings_name is not None:
            pyver = '.'.join(str(e) for e in sys.version_info[0:3])
            appname = 'ephyviewer'+'_py'+pyver
            self.settings = QT.QSettings(appname, self.settings_name)
        
        self.setDockNestingEnabled(True) 
        
        
        self.viewers = OrderedDict()
        
        self.navigation_toolbar = NavigationToolBar(**navigation_params)
        dock = QT.QDockWidget('navigation',self)
        dock.setObjectName( 'navigation')
        dock.setWidget(self.navigation_toolbar)
        dock.setTitleBarWidget(QT.QWidget())
        self.addDockWidget(QT.TopDockWidgetArea, dock)
        
        self.navigation_toolbar.time_changed.connect(self.on_time_changed)
        self.navigation_toolbar.xsize_changed.connect(self.on_xsize_changed)

    def add_view(self, widget, location='bottom', orientation='vertical',
                        tabify_with=None, split_with=None):
        name = widget.name
        
        assert name not in self.viewers, 'Viewer already in MainViewer'
        
        dock = QT.QDockWidget(name)
        dock.setObjectName(name)
        dock.setWidget(widget)

        
        if tabify_with is not None:
            assert tabify_with in self.viewers, '{} no exists'.format(tabify_with)
            #~ raise(NotImplementedError)
            #tabifyDockWidget ( QDockWidget * first, QDockWidget * second )
            other_dock = self.viewers[tabify_with]['dock']
            self.tabifyDockWidget(other_dock, dock)
            
        elif split_with is not None:
            assert split_with in self.viewers, '{} no exists'.format(split_with)
            #~ raise(NotImplementedError)
            orien = orientation_to_qt[orientation]
            other_dock = self.viewers[split_with]['dock']
            self.splitDockWidget(other_dock, dock, orien)
            #splitDockWidget ( QDockWidget * first, QDockWidget * second, Qt::Orientation orientation )
        else:
            loc = location_to_qt[location]
            orien = orientation_to_qt[orientation]
            #~ print(location, loc)
            self.addDockWidget(loc, dock, orien)

        self.viewers[name] = {'widget': widget, 'dock':dock}
        
        widget.time_changed.connect(self.on_time_changed)
        
        try:
            t_start = min(self.navigation_toolbar.t_start, widget.source.t_start)
            t_stop = max(self.navigation_toolbar.t_stop, widget.source.t_stop)
            print('t_start, t_stop', t_start, t_stop, name)
            self.navigation_toolbar.set_start_stop(t_start, t_stop, seek=True)
        except:
            print('impossiblie to set t_start t_stop')
        
        if self.settings_name is not None:
            value = self.settings.value('viewer_'+name)
            if value is not None:
                #~ try:
                if True:
                    value = pickle.loads(value)
                    print('setiings', name, value)
                    widget.set_settings(value)
                    
                #~ except:
                    #~ print('erreur settings', name)
            
            #~ print(value)
            
        

    def on_time_changed(self, t):
        
        for name , viewer in self.viewers.items():
            if viewer['widget'] != self.sender():
                t0 = time.time()
                viewer['widget'].seek(t)
                
                if self.debug:
                    t1 = time.time()
                    print('refresh duration for', name, t1-t0, 's')
        
        if self.navigation_toolbar != self.sender():
            #~ print('self.navigation_toolbar.seek', t)
            self.navigation_toolbar.seek(t, emit=False)
    
    def on_xsize_changed(self, xsize):
        print('on_xsize_changed', xsize)
        for name , viewer in self.viewers.items():
            if hasattr(viewer['widget'], 'set_xsize'):
                viewer['widget'].set_xsize(xsize)
    
    def seek(self, t):
        for name , viewer in self.viewers.items():
            viewer['widget'].seek(t)
        
        self.navigation_toolbar.seek(t, emit=False)
    
    def closeEvent(self, event):
        #~ print('save settings')
        event.accept()
        
        if self.settings_name is not None:
            
            for name, d in self.viewers.items():
                value = d['widget'].get_settings()
                if value is not None:
                    print('save ', name)
                    self.settings.setValue('viewer_'+name, pickle.dumps(value))
