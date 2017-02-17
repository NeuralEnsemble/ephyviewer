# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

from .myqt import QT
import pyqtgraph as pg
import numpy as np

from collections import OrderedDict

import time

class NavigationToolBar(QT.QWidget) :
    """
    """
    time_changed = QT.pyqtSignal(float)
    
    def __init__(self, parent = None, show_play = True, show_step = True,
                                    show_scroll_time = True, show_spinbox = True, show_label = False,
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
        self.show_label = show_label
        self.play_interval = play_interval
        

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
        self.mainlayout.addLayout(h)
        
        if show_play:
            but = QT.QPushButton(icon=QT.QIcon.fromTheme('media-playback-start'))
            but.clicked.connect(self.on_play)
            h.addWidget(but)
            
            but = QT.QPushButton(icon=QT.QIcon.fromTheme('media-playback-stop'))
            #~ but = QT.QPushButton(QT.QIcon(':/media-playback-stop.png'), '')
            but.clicked.connect(self.on_stop_pause)
            h.addWidget(but)
            
            h.addWidget(QT.QLabel('Speed:'))
            self.speedSpin = pg.SpinBox(bounds=(0.01, 100.), step=0.1, value=1.)
            h.addWidget(self.speedSpin)
            self.speedSpin.valueChanged.connect(self.on_change_speed)
            
            self.speed = 1.
            
            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))
            
        
        self.steps = ['60s','10s', '1s', '100ms', '50ms', '5ms' ]
        
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
            
            
            #~ self.popupStep = QT.QToolButton( popupMode = QToolButton.MenuButtonPopup,
                                                                        #~ toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                                                        #~ text = u'Step 50ms'
                                                                        #~ )
            #~ t.addWidget(self.popupStep)
            #~ ag = QT.QActionGroup(self.popupStep )
            #~ ag.setExclusive( True)
            #~ for s in ['60s','10s', '1s', '100ms', '50ms', '5ms' ]:
                #~ act = QT.QAction(s, self.popupStep, checkable = True)
                #~ ag.addAction(act)
                #~ self.popupStep.addAction(act)
            #~ ag.triggered.connect(self.change_step)
            
            but = QT.QPushButton('>')
            but.clicked.connect(self.next_step)
            h.addWidget(but)
            
            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))

        

        
        if show_spinbox:
            self.spinbox_time =pg.SpinBox(decimals = 8, bounds = (-np.inf, np.inf),step = 0.05, siPrefix=False, suffix='s', int=False)
            h.addWidget(self.spinbox_time)
            #trick for separator
            h.addWidget(QT.QFrame(frameShape=QT.QFrame.VLine, frameShadow=QT.QFrame.Sunken))
            
            
            #~ h.addSeparator()
            self.spinbox_time.valueChanged.connect(self.on_spinbox_time_changed)
        
        if show_label:
            self.label_time = QT.QLabel('0')
            t.addWidget(self.label_time)
            t.addSeparator()

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
        else:
            self.step_size = float(text[:-1])
        print('self.step_size', self.step_size)
        
    def prev_step(self):
        t = self.t -  self.step_size
        self.seek(t)
    
    def next_step(self):
        t = self.t +  self.step_size
        self.seek(t)
    
    def on_scroll_time_changed(self, pos):
        t = pos/1000.*(self.t_stop - self.t_start)+self.t_start
        self.seek(t, refresh_scroll = False)
    
    def on_spinbox_time_changed(self, val):
        self.seek(val, refresh_spinbox = False)
    
    def seek(self , t, refresh_scroll = True, refresh_spinbox = True):
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
        
        if self.show_label:
            self.label_time.setText('{:5.3} s'.format(self.t))
            
        self.time_changed.emit(self.t)
        
    def on_change_speed(self , speed):
        self.speed = speed
    
    
