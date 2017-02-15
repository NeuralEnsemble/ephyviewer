# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

from collections import OrderedDict

from .myqt import QT


location_to_qt={
    'left': QT.LeftDockWidgetArea,
    'right': QT.RightDockWidgetArea,
    'top': QT.TopDockWidgetArea,
    'bottom': QT.BottomDockWidgetArea
}

orientation_to_qt={
    'horizontal': QT.Horizontal,
    'vertical': QT.Vertical,
}


class MainViewer(QT.QMainWindow):
    def __init__(self):
        QT.QMainWindow.__init__(self)

        #TODO settings
        #http://www.programcreek.com/python/example/86789/PyQt5.QtCore.QSettings
        
        
        self.setDockNestingEnabled(True) 
        
        
        self.viewers = OrderedDict()
        
        
        
        #~ self.timeseeker = TimeSeeker()
        #~ dock = QDockWidget('Time',self)
        #~ dock.setObjectName( 'Time')
        #~ dock.setWidget(self.timeseeker)
        #~ self.addDockWidget(Qt.TopDockWidgetArea, dock)

        #~ self.timeseeker.time_changed.connect(self.seek_all)
        #~ self.timeseeker.fast_time_changed.connect(self.fast_seek_all)
        
        #~ self.subviewers = [ ]
    
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





