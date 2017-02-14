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
    
    def add_view(self, widget, name, location='bottom', orientation='vertical',
                        tabify_with=None, split_with=None):
        assert name not in self.viewers, 'Viewer already in MainViewer'
        
        dock = QT.QDockWidget(name)
        dock.setObjectName(name)
        dock.setWidget(widget)

        
        if tabify_with is not None:
            raise(NotImplementedError)
            #tabifyDockWidget ( QDockWidget * first, QDockWidget * second )
        elif split_with is not None:
            raise(NotImplementedError)
            #splitDockWidget ( QDockWidget * first, QDockWidget * second, Qt::Orientation orientation )
        else:
            loc = location_to_qt[location]
            orien = orientation_to_qt[orientation]
            self.addDockWidget(loc, dock, orien)

        self.viewers[name] = {'widget': widget, 'dock':dock}





