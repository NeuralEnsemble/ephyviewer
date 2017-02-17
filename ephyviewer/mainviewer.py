# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

from collections import OrderedDict
import time

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
    def __init__(self, debug=False):
        QT.QMainWindow.__init__(self)

        #TODO settings
        #http://www.programcreek.com/python/example/86789/PyQt5.QtCore.QSettings
        
        self.debug = debug
        
        self.setDockNestingEnabled(True) 
        
        
        self.viewers = OrderedDict()
        
        self.navigation_toolbar = NavigationToolBar()
        dock = QT.QDockWidget('navigation',self)
        dock.setObjectName( 'navigation')
        dock.setWidget(self.navigation_toolbar)
        dock.setTitleBarWidget(QT.QWidget())
        self.addDockWidget(QT.TopDockWidgetArea, dock)
        self.navigation_toolbar.time_changed.connect(self.on_time_changed)

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
            self.addDockWidget(loc, dock, orien)

        self.viewers[name] = {'widget': widget, 'dock':dock}
        
        #TODO seg_num
        try:
            t_start = min(self.navigation_toolbar.t_start, widget.source.get_t_start(seg_num=0))
            t_stop = max(self.navigation_toolbar.t_start, widget.source.get_t_stop(seg_num=0))
            #~ print('t_start, t_stop', t_start, t_stop)
            self.navigation_toolbar.set_start_stop(t_start, t_stop, seek=True)
        except:
            print('impossiblie to set t_start t_stop')
        

    def on_time_changed(self, t):
        
        for name , viewer in self.viewers.items():
            if viewer['widget'] != self.sender():
                t0 = time.time()
                viewer['widget'].seek(t)
                
                if self.debug:
                    t1 = time.time()
                    print('refresh duration for', name, t1-t0, 's')
        
        if self.navigation_toolbar != self.sender():
            print('self.navigation_toolbar.seek', t)
            self.navigation_toolbar.seek(t)
        


