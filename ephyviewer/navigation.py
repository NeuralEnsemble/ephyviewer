# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from .myqt import QT
import pyqtgraph as pg
import numpy as np

from collections import OrderedDict

import time
import datetime


#TODO:
#  * xsize in navigation
#  * real time when possible

class NavigationToolBar(QT.QWidget) :
    """
    """
    time_changed = QT.pyqtSignal(float)
    xsize_changed = QT.pyqtSignal(float)
    auto_scale_requested = QT.pyqtSignal()

    def __init__(self, parent=None, show_play=True, show_step=True,
                                    show_scroll_time=True, show_spinbox=True,
                                    show_label_datetime=False, datetime0=None,
                                    datetime_format='%Y-%m-%d %H:%M:%S',
                                    show_global_xsize=True, show_auto_scale=True,
                                    play_interval = 0.1) :

        QT.QWidget.__init__(self, parent)

        self.setSizePolicy(QT.QSizePolicy.Minimum, QT.QSizePolicy.Maximum)

        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)



        #~ self.toolbar = QT.QToolBar()
        #~ self.mainlayout.addWidget(self.toolbar)
        #~ t = self.toolbar

        self.show_play = show_play
        self.show_step = show_step
        self.show_scroll_time = show_scroll_time
        self.show_spinbox = show_spinbox
        self.show_label_datetime = show_label_datetime
        self.show_global_xsize = show_global_xsize
        self.play_interval = play_interval

        self.datetime0 = datetime0
        self.datetime_format = datetime_format


        if show_scroll_time:
            #~ self.slider = QSlider()
            self.scroll_time = QT.QScrollBar(orientation=QT.Horizontal, minimum=0, maximum=1000)
            self.mainlayout.addWidget(self.scroll_time)
            self.scroll_time.valueChanged.connect(self.on_scroll_time_changed)

            #TODO min/max/step
            #~ self.scroll_time.valueChanged.disconnect(self.on_scroll_time_changed)
            #~ self.scroll_time.setValue(int(sr*t))
            #~ self.scroll_time.setPageStep(int(sr*self.xsize))
            #~ self.scroll_time.valueChanged.connect(self.on_scroll_time_changed)
            #~ self.scroll_time.setMinimum(0)
            #~ self.scroll_time.setMaximum(length)

        h = QT.QHBoxLayout()
        h.addStretch()
        self.mainlayout.addLayout(h)

        if show_play:
            but = QT.QPushButton(icon=QT.QIcon(':/media-playback-start.svg'))
            but.clicked.connect(self.on_play)
            h.addWidget(but)

            but = QT.QPushButton(icon=QT.QIcon(':/media-playback-stop.svg'))
            #~ but = QT.QPushButton(QT.QIcon(':/media-playback-stop.png'), '')
            but.clicked.connect(self.on_stop_pause)
            h.addWidget(but)

            h.addWidget(QT.QLabel('Speed:'))
            self.speedSpin = pg.SpinBox(bounds=(0.01, 100.), step=0.1, value=1.)
            if 'compactHeight' in self.speedSpin.opts:  # pyqtgraph >= 0.11.0
                self.speedSpin.setOpts(compactHeight=False)
            h.addWidget(self.speedSpin)
            self.speedSpin.valueChanged.connect(self.on_change_speed)

            self.speed = 1.

            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))

            # add spacebar shortcut for play/pause
            play_pause_shortcut = QT.QShortcut(self)
            play_pause_shortcut.setKey(QT.QKeySequence(' '))
            play_pause_shortcut.activated.connect(self.on_play_pause_shortcut)

        self.steps = ['60 s', '10 s', '1 s', '100 ms', '50 ms', '5 ms', '1 ms', '200 us']

        if show_step:
            but = QT.QPushButton('<')
            but.clicked.connect(self.prev_step)
            h.addWidget(but)

            self.combo_step = QT.QComboBox()
            self.combo_step.addItems(self.steps)
            self.combo_step.setCurrentIndex(2)
            h.addWidget(self.combo_step)

            self.on_change_step(None)
            self.combo_step.currentIndexChanged.connect(self.on_change_step)

            but = QT.QPushButton('>')
            but.clicked.connect(self.next_step)
            h.addWidget(but)

            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))

            # add shortcuts for stepping through time and changing step size
            shortcuts = [
                {'key': QT.Qt.Key_Left,  'callback': self.prev_step},
                {'key': QT.Qt.Key_Right, 'callback': self.next_step},
                {'key': QT.Qt.Key_Up,    'callback': self.increase_step},
                {'key': QT.Qt.Key_Down,  'callback': self.decrease_step},
                {'key': 'a',             'callback': self.prev_step},
                {'key': 'd',             'callback': self.next_step},
                {'key': 'w',             'callback': self.increase_step},
                {'key': 's',             'callback': self.decrease_step},
            ]
            for s in shortcuts:
                shortcut = QT.QShortcut(self)
                shortcut.setKey(QT.QKeySequence(s['key']))
                shortcut.activated.connect(s['callback'])


        if show_spinbox:
            h.addWidget(QT.QLabel('Time (s):'))
            self.spinbox_time =pg.SpinBox(decimals = 8, bounds = (-np.inf, np.inf),step = 0.05, siPrefix=False, suffix='', int=False)
            if 'compactHeight' in self.spinbox_time.opts:  # pyqtgraph >= 0.11.0
                self.spinbox_time.setOpts(compactHeight=False)
            h.addWidget(self.spinbox_time)
            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))


            #~ h.addSeparator()
            self.spinbox_time.valueChanged.connect(self.on_spinbox_time_changed)

        if show_label_datetime:
            assert self.datetime0 is not None
            self.label_datetime = QT.QLabel('')
            h.addWidget(self.label_datetime)
            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))

        if show_global_xsize:
            h.addWidget(QT.QLabel('Time width (s):'))
            self.spinbox_xsize =pg.SpinBox(value=3., decimals = 8, bounds = (0.001, np.inf),step = 0.1, siPrefix=False, suffix='', int=False)
            if 'compactHeight' in self.spinbox_xsize.opts:  # pyqtgraph >= 0.11.0
                self.spinbox_xsize.setOpts(compactHeight=False)
            h.addWidget(self.spinbox_xsize)
            #~ self.spinbox_xsize.valueChanged.connect(self.on_spinbox_xsize_changed)
            self.spinbox_xsize.valueChanged.connect(self.xsize_changed.emit)
            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))

        if show_auto_scale:
            but = QT.PushButton('Auto scale')
            h.addWidget(but)
            but.clicked.connect(self.auto_scale_requested.emit)
            #~ h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))

        h.addStretch()

        self.timer_play = QT.QTimer(parent=self, interval=int(play_interval*1000))
        self.timer_play.timeout.connect(self.on_timer_play_interval)
        self.timer_delay = None

        # all in s

        self.t = 0 #  s
        self.set_start_stop(0., 0.1)

        self.last_time = None

    def on_play(self):
        self.last_time = time.time()
        self.timer_play.start()

    def on_stop_pause(self):
        self.timer_play.stop()
        self.seek(self.t)

    def on_play_pause_shortcut(self):
        if self.timer_play.isActive():
            self.on_stop_pause()
        else:
            self.on_play()

    def on_timer_play_interval(self):
        actual_time = time.time()
        #~ t = self.t +  self.play_interval*self.speed
        t = self.t +  (actual_time-self.last_time)*self.speed
        self.seek(t)
        self.last_time = actual_time

    def set_start_stop(self, t_start, t_stop, seek = True):
        #~ print 't_start', t_start, 't_stop', t_stop
        assert t_stop>t_start
        self.t_start = t_start
        self.t_stop = t_stop
        if seek:
            self.seek(self.t_start)
        if self.show_spinbox:
            self.spinbox_time.setMinimum(t_start)
            self.spinbox_time.setMaximum(t_stop)

    def on_change_step(self, val):
        text = str(self.combo_step.currentText ())

        if text.endswith('ms'):
            self.step_size = float(text[:-2])*1e-3
        elif text.endswith('us'):
            self.step_size = float(text[:-2])*1e-6
        else:
            self.step_size = float(text[:-1])
        #~ print('self.step_size', self.step_size)

    def prev_step(self):
        t = self.t -  self.step_size
        self.seek(t)

    def next_step(self):
        t = self.t +  self.step_size
        self.seek(t)

    def increase_step(self):
        new_index = max(self.combo_step.currentIndex()-1, 0)
        self.combo_step.setCurrentIndex(new_index)

    def decrease_step(self):
        new_index = min(self.combo_step.currentIndex()+1, self.combo_step.count()-1)
        self.combo_step.setCurrentIndex(new_index)

    def on_scroll_time_changed(self, pos):
        t = pos/1000.*(self.t_stop - self.t_start)+self.t_start
        self.seek(t, refresh_scroll = False)

    def on_spinbox_time_changed(self, val):
        self.seek(val, refresh_spinbox = False)

    #~ def on_spinbox_xsize_changed(self, val):
        #~ print('xsize', val)

    def seek(self , t, refresh_scroll = True, refresh_spinbox = True, emit=True):
        self.t = t
        if (self.t<self.t_start):
            self.t = self.t_start
        if (self.t>self.t_stop):
            self.t = self.t_stop
            if self.timer_play.isActive():
                self.timer_play.stop()
                #~ self.stop_pause()

        if refresh_scroll and self.show_scroll_time:
            self.scroll_time.valueChanged.disconnect(self.on_scroll_time_changed)
            pos = int((self.t - self.t_start)/(self.t_stop - self.t_start)*1000.)
            self.scroll_time.setValue(pos)
            self.scroll_time.valueChanged.connect(self.on_scroll_time_changed)

        if refresh_spinbox and self.show_spinbox:
            self.spinbox_time.valueChanged.disconnect(self.on_spinbox_time_changed)
            self.spinbox_time.setValue(t)
            self.spinbox_time.valueChanged.connect(self.on_spinbox_time_changed)

        if self.show_label_datetime:
            dt = self.datetime0 + datetime.timedelta(seconds=self.t)
            self.label_datetime.setText(dt.strftime(self.datetime_format))


        if emit:
            self.time_changed.emit(self.t)

    def on_change_speed(self , speed):
        self.speed = speed

    def set_settings(self, d):
        if hasattr(self, 'spinbox_xsize') and 'xsize' in d:
            self.spinbox_xsize.setValue(d['xsize'])

    def get_settings(self):
        d = {}
        if hasattr(self, 'spinbox_xsize'):
            d['xsize'] = float(self.spinbox_xsize.value())
        return d
