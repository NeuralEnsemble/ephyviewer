# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from collections import OrderedDict
import time
import sys
import pickle

from .myqt import QT, QT_MODE
from .navigation import NavigationToolBar

from .traceviewer import TraceViewer
from .epochviewer import EpochViewer
from .eventlist import EventList
from .spiketrainviewer import SpikeTrainViewer

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
    def __init__(self, debug=False, settings_name=None, parent=None, global_xsize_zoom=False, **navigation_params):
        QT.QMainWindow.__init__(self, parent)

        #TODO settings
        #http://www.programcreek.com/python/example/86789/PyQt5.QtCore.QSettings

        self.debug = debug
        if self.debug:
            print('debug True')
        self.settings_name = settings_name
        if self.settings_name is not None:
            pyver = '.'.join(str(e) for e in sys.version_info[0:3])
            appname = 'ephyviewer'+'_py'+pyver
            self.settings = QT.QSettings(appname, self.settings_name)
        self.global_xsize_zoom = global_xsize_zoom

        self.setDockNestingEnabled(True)


        self.viewers = OrderedDict()

        self.navigation_toolbar = NavigationToolBar(**navigation_params)

        dock = self.navigation_dock =  QT.QDockWidget('navigation',self)
        dock.setObjectName( 'navigation')
        dock.setWidget(self.navigation_toolbar)
        dock.setTitleBarWidget(QT.QWidget())
        self.addDockWidget(QT.TopDockWidgetArea, dock)

        self.navigation_toolbar.time_changed.connect(self.on_time_changed)
        self.navigation_toolbar.xsize_changed.connect(self.on_xsize_changed)
        self.navigation_toolbar.auto_scale_requested.connect(self.auto_scale)

        self.load_one_setting('navigation_toolbar', self.navigation_toolbar)


    def add_view(self, widget, location='bottom', orientation='vertical',
                        tabify_with=None, split_with=None):
        name = widget.name

        assert name not in self.viewers, 'Viewer already in MainViewer'

        dock = QT.QDockWidget(name)
        dock.setObjectName(name)
        dock.setWidget(widget)

        #TODO chustum titlebar
        #~ dock.setTitleBarWidget(titlebar)

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

        self.load_one_setting(name, widget)

        widget.time_changed.connect(self.on_time_changed)
        if self.global_xsize_zoom and hasattr(widget, 'params_controller'):
            widget.params_controller.xsize_zoomed.connect(self.set_xsize)

        if hasattr(widget.source, 't_start'):
            # quick fix for DataFrameView should be removed with betetr solution
            if len(self.viewers) ==1:
                # first widget
                t_start, t_stop = widget.source.t_start, widget.source.t_stop
            else:
                    t_start = min(self.navigation_toolbar.t_start, widget.source.t_start)
                    t_stop = max(self.navigation_toolbar.t_stop, widget.source.t_stop)
            self.navigation_toolbar.set_start_stop(t_start, t_stop, seek=True)



    def load_one_setting(self, name, widget):
        #~ print('load_one_setting', name, self.settings_name)
        if self.settings_name is not None:
            value = self.settings.value('viewer_'+name)
            #~ print('value', value)
            if value is not None:
                try:
                #~ if True:
                    if QT_MODE == 'PyQt4' and sys.version_info[0]==2:
                        if type(value)==QT.QVariant:
                            value = bytes(value.toPyObject())
                    value = pickle.loads(value)
                    widget.set_settings(value)
                except:
                    print('erreur load settings', name)


    def save_all_settings(self):
        if self.debug:
            print('save_all_settings')
        if self.settings_name is not None:
            for name, d in self.viewers.items():
                value = d['widget'].get_settings()
                #~ print('save', name, type(value))
                if value is not None:
                    #~ print('save ', name)
                    self.settings.setValue('viewer_'+name, pickle.dumps(value))
            value = self.navigation_toolbar.get_settings()
            if value is not None:
                #~ print('save ', 'navigation_toolbar')
                self.settings.setValue('viewer_navigation_toolbar', pickle.dumps(value))

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
        #~ print('on_xsize_changed', xsize)
        for name , viewer in self.viewers.items():
            if hasattr(viewer['widget'], 'set_xsize'):
                viewer['widget'].set_xsize(xsize)

    def auto_scale(self):
        #~ print('on_xsize_changed', xsize)
        for name , viewer in self.viewers.items():
            if hasattr(viewer['widget'], 'auto_scale'):
                viewer['widget'].auto_scale()


    def seek(self, t):
        for name , viewer in self.viewers.items():
            viewer['widget'].seek(t)

        self.navigation_toolbar.seek(t, emit=False)

    def set_xsize(self, xsize):
        if hasattr(self.navigation_toolbar, 'spinbox_xsize'):
            self.navigation_toolbar.spinbox_xsize.setValue(xsize)
        #~ self.on_xsize_changed(xsize)

    def closeEvent(self, event):
        for name , viewer in self.viewers.items():
            viewer['widget'].close()
        self.save_all_settings()
        event.accept()





def compose_mainviewer_from_sources(sources, mainviewer=None):
    """
    Helper that compose a windows from several source with basic rules.

    Use internally in:
      * standalone
      * when generating mainviewer from neo segment

    """

    if mainviewer is None:
        mainviewer = MainViewer(show_auto_scale=True)

    for i, sig_source in enumerate(sources['signal']):
        view = TraceViewer(source=sig_source, name='signal {}'.format(i))
        view.params['scale_mode'] = 'same_for_all'
        view.params['display_labels'] = True
        if i==0:
            mainviewer.add_view(view)
        else:
            mainviewer.add_view(view, tabify_with='signal {}'.format(i-1))
        view.auto_scale()


    for i, spike_source in enumerate(sources['spike']):
        view = SpikeTrainViewer(source=spike_source, name='spikes')
        mainviewer.add_view(view)

    for i, ep_source in enumerate(sources['epoch']):
        view = EpochViewer(source=ep_source, name='epochs')
        mainviewer.add_view(view)

    if 'event' in sources and len(sources['event']) > 0:
        ev_source_list = sources['event']
    else:
        ev_source_list = sources['epoch']
    for i, ev_source in enumerate(ev_source_list):
        view = EventList(source=ev_source, name='Event list')
        mainviewer.add_view(view, location='bottom',  orientation='horizontal')


    return mainviewer
