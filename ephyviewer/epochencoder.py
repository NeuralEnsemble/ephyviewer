# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from copy import deepcopy
from collections import deque

import numpy as np

import matplotlib.cm
import matplotlib.colors

from .myqt import QT
from . import tools

import pyqtgraph as pg

from .base import ViewerBase, Base_ParamController, MyViewBox, same_param_tree
from .epochviewer import RectItem, DataGrabber
from .datasource import WritableEpochSource


default_params = [
    {'name': 'xsize', 'type': 'float', 'value': 3., 'step': 0.1},
    {'name': 'xratio', 'type': 'float', 'value': 0.3, 'step': 0.1, 'limits': (0,1)},
    {'name': 'background_color', 'type': 'color', 'value': 'k'},
    {'name': 'vline_color', 'type': 'color', 'value': '#FFFFFFAA'},
    {'name': 'label_fill_color', 'type': 'color', 'value': '#222222DD'},
    {'name': 'label_size', 'type': 'int', 'value': 8, 'limits': (1,np.inf)},
    {'name': 'new_epoch_step', 'type': 'float', 'value': .1, 'step': 0.1, 'limits':(0,np.inf)},
    {'name': 'exclusive_mode', 'type': 'bool', 'value': True},
    {'name': 'view_mode', 'type': 'list', 'value':'stacked', 'values' : ['stacked', 'flat']},
    {'name': 'keys_as_ticks', 'type': 'bool', 'value': True},
    {'name': 'undo_history_size', 'type': 'int', 'value': 500, 'limits': (1, np.inf)},

    #~ {'name': 'display_labels', 'type': 'bool', 'value': True},
    ]

SEEK_COL = 0
START_COL = 1
STOP_COL = 2
DURATION_COL = 3
LABEL_COL = 4
SPLIT_COL = 5
DUPLICATE_COL = 6
DELETE_COL = 7



class EpochEncoder_ParamController(Base_ParamController):
    def __init__(self, parent=None, viewer=None, with_visible=True, with_color=True):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)

        self.resize(400, 700)

        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)

        self.v1 = QT.QVBoxLayout()
        h.addLayout(self.v1)
        self.tree_params = pg.parametertree.ParameterTree()
        self.tree_params.setParameters(self.viewer.params, showTop=True)
        self.tree_params.header().hide()
        self.v1.addWidget(self.tree_params, stretch = 1)

        self.tree_label_params = pg.parametertree.ParameterTree()
        self.tree_label_params.setParameters(self.viewer.by_label_params, showTop=True)
        self.tree_label_params.header().hide()
        self.v1.addWidget(self.tree_label_params, stretch = 3)

        self.btn_new_label = QT.PushButton('New label')
        self.btn_new_label.clicked.connect(self.create_new_label)
        self.v1.addWidget(self.btn_new_label)

    def create_new_label(self):
        label, ok = QT.QInputDialog.getText(self, 'New label', 'Enter a new label:')

        # abort if user cancelled or typed nothing
        if not ok or not label: return

        # abort if label already exists
        if label in self.viewer.source.possible_labels: return

        # TODO: determine color from a color map?
        color = (120, 120, 120) # gray

        # add new label to WritableEpochSource
        self.viewer.source.possible_labels.append(label)
        self.viewer.source.color_labels.append(color)

        # get next unused shortcut key
        used_keys = [p['key'] for p in self.viewer.by_label_params]
        unused_keys = [k for k in '1234567890' if k not in used_keys]
        key = unused_keys[0] if len(unused_keys)>0 else ''

        # assign shortcuts without and with modifier key
        self.viewer.assign_label_shortcuts(label, key)

        # add new label to params
        name = 'label{}'.format(len(self.viewer.source.possible_labels)-1)
        children = [
            {'name': 'name', 'type': 'str', 'value': label, 'readonly':True},
            {'name': 'color', 'type': 'color', 'value': self.source.color_by_label(label)},
            {'name': 'key', 'type': 'str', 'value': key},
        ]
        self.viewer.by_label_params.addChild({'name': name, 'type': 'group', 'children': children})

        # clear and redraw plot to update labels and plot range
        self.viewer.plot.clear()
        self.viewer.initialize_plot()
        self.viewer.refresh()

        # add new label to range selector dropdown menu
        self.viewer.combo_labels.addItems([label])

        # refresh table to add new label to all label dropdown menus
        self.viewer.refresh_table()



class EpochEncoder(ViewerBase):
    _default_params = default_params

    request_data = QT.pyqtSignal(float, float, object)

    def __init__(self, **kargs):
        ViewerBase.__init__(self, **kargs)

        assert isinstance(self.source, WritableEpochSource)

        self.label_shortcuts = {}

        self.make_params()
        self.make_param_controller()
        self.set_layout()

        self.viewBox.doubleclicked.connect(self.show_params_controller)

        self.initialize_plot()

        self.on_range_visibility_changed(refresh=False)



        self.thread = QT.QThread(parent=self)
        self.datagrabber = DataGrabber(source=self.source)
        self.datagrabber.moveToThread(self.thread)
        self.thread.start()


        self.datagrabber.data_ready.connect(self.on_data_ready)
        self.request_data.connect(self.datagrabber.on_request_data)

        self.table_button_fixed_width = 32
        self.refresh_table()

        self.history = deque(maxlen=self.params['undo_history_size'])
        self.history_position = 0
        self.changes_since_save = 0
        self.append_history()

        # reverse the automatic increment of changes_since_save done by
        # append_history, then disable the save button
        self.changes_since_save = 0
        self.save_action.setEnabled(False)


    def make_params(self):
        # Create parameters
        self.params = pg.parametertree.Parameter.create(name='Global options',
                                                    type='group', children=self._default_params)
        self.params.param('xsize').setLimits((0, np.inf))


        keys = '1234567890'
        all = []
        for i, label in enumerate(self.source.possible_labels):
            # get string for shortcut key
            key = keys[i] if i<len(keys) else ''

            name = 'label{}'.format(i)
            children = [
                {'name': 'name', 'type': 'str', 'value': label, 'readonly':True},
                {'name': 'color', 'type': 'color', 'value': self.source.color_by_label(label)},
                {'name': 'key', 'type': 'str', 'value': key},
            ]
            all.append({'name': name, 'type': 'group', 'children': children})

            # assign shortcuts without and with modifier key
            self.assign_label_shortcuts(label, key)

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

        self.controls = QT.QWidget()
        self.controls.setSizePolicy(QT.QSizePolicy.Preferred, QT.QSizePolicy.Fixed)
        self.mainlayout.addWidget(self.controls)

        h = QT.QHBoxLayout()
        h.setContentsMargins(5, 5, 0, 0)
        h.setSpacing(5)
        self.controls.setLayout(h)

        # Range box

        self.range_group_box = QT.QGroupBox('Time &range selector', checkable=True, checked=False)
        self.range_group_box.clicked.connect(self.on_range_visibility_changed)
        h.addWidget(self.range_group_box)

        range_group_box_layout = QT.QGridLayout()
        range_group_box_layout.setSpacing(0)
        self.range_group_box.setLayout(range_group_box_layout)

        range_shortcut = QT.QShortcut(self)
        range_shortcut.setKey(QT.QKeySequence('r'))
        range_shortcut.activated.connect(self.range_group_toggle)
        self.range_group_box.setToolTip('Toggle with shortcut: r')

        spinboxs = []
        buts = []
        for i, but_text in enumerate(['Set start >', 'Set stop >']):
            but = QT.QPushButton(but_text)
            buts.append(but)
            range_group_box_layout.addWidget(but, i, 0)
            spinbox = pg.SpinBox(value=float(i), decimals = 8, bounds = (-np.inf, np.inf),step = 0.05, siPrefix=False, int=False)
            if 'compactHeight' in spinbox.opts:  # pyqtgraph >= 0.11.0
                spinbox.setOpts(compactHeight=False)
            range_group_box_layout.addWidget(spinbox, i, 1)
            spinbox.setSizePolicy(QT.QSizePolicy.Preferred, QT.QSizePolicy.Preferred, )
            spinbox.valueChanged.connect(self.on_spin_limit_changed)
            spinboxs.append(spinbox)
        self.spin_limit1, self.spin_limit2 = spinboxs
        buts[0].clicked.connect(self.set_limit1)
        buts[1].clicked.connect(self.set_limit2)

        limit1_shortcut = QT.QShortcut(self)
        limit1_shortcut.setKey(QT.QKeySequence('['))
        limit1_shortcut.activated.connect(buts[0].click)
        buts[0].setToolTip('Set start with shortcut: [')

        limit2_shortcut = QT.QShortcut(self)
        limit2_shortcut.setKey(QT.QKeySequence(']'))
        limit2_shortcut.activated.connect(buts[1].click)
        buts[1].setToolTip('Set stop with shortcut: ]')

        self.combo_labels = QT.QComboBox()
        self.combo_labels.addItems(self.source.possible_labels)
        range_group_box_layout.addWidget(self.combo_labels, 2, 0, 1, 2)

        self.but_apply_region = QT.PushButton('Insert within range')
        range_group_box_layout.addWidget(self.but_apply_region, 3, 0, 1, 2)
        self.but_apply_region.clicked.connect(self.apply_region)
        self.but_apply_region.setToolTip('Insert with customizable shortcuts (see options)')

        self.but_del_region = QT.PushButton('Clear within range')
        range_group_box_layout.addWidget(self.but_del_region, 4, 0, 1, 2)
        self.but_del_region.clicked.connect(self.delete_region)

        # Table

        self.table_widget = QT.QTableWidget()
        h.addWidget(self.table_widget, stretch=1)
        self.table_widget.setSelectionMode(QT.QAbstractItemView.SingleSelection)
        self.table_widget.setSelectionBehavior(QT.QAbstractItemView.SelectRows)
        self.table_widget.cellClicked.connect(self.on_table_cell_click)
        self.table_widget.cellChanged.connect(self.on_table_cell_change)
        self.table_widget_icons = {
            'seek': QT.QIcon(':/epoch-encoder-seek.svg'),
            'split': QT.QIcon(':/epoch-encoder-split.svg'),
            'duplicate': QT.QIcon(':/epoch-encoder-duplicate.svg'),
            'delete': QT.QIcon(':/epoch-encoder-delete.svg'),
        }

        # Toolbar

        self.toolbar = QT.QToolBar()
        self.toolbar.setToolButtonStyle(QT.Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QT.QSize(16, 16))
        self.mainlayout.addWidget(self.toolbar)

        self.toggle_controls_visibility_action = self.toolbar.addAction('Hide controls', self.on_controls_visibility_changed)
        self.toggle_controls_visibility_button = self.toolbar.widgetForAction(self.toggle_controls_visibility_action)
        self.toggle_controls_visibility_button.setArrowType(QT.UpArrow)

        self.toolbar.addSeparator()

        self.save_action = self.toolbar.addAction('Save', self.on_save)
        self.save_action.setShortcut('Ctrl+s')  # automatically converted to Cmd+s on Mac
        self.save_action.setToolTip('Save with shortcut: Ctrl/Cmd+s')
        self.save_action.setIcon(QT.QIcon(':/epoch-encoder-save.svg'))

        self.undo_action = self.toolbar.addAction('Undo', self.on_undo)
        self.undo_action.setShortcut('Ctrl+z')  # automatically converted to Cmd+z on Mac
        self.undo_action.setToolTip('Undo with shortcut: Ctrl/Cmd+z')
        self.undo_action.setIcon(QT.QIcon(':/epoch-encoder-undo.svg'))

        self.redo_action = self.toolbar.addAction('Redo', self.on_redo)
        self.redo_action.setShortcut('Ctrl+y')  # automatically converted to Cmd+y on Mac
        self.redo_action.setToolTip('Redo with shortcut: Ctrl/Cmd+y')
        self.redo_action.setIcon(QT.QIcon(':/epoch-encoder-redo.svg'))

        self.toolbar.addAction('Options', self.show_params_controller)

        self.toolbar.addAction('New label', self.params_controller.create_new_label)

        self.toolbar.addAction('Merge neighbors', self.on_merge_neighbors)

        self.toolbar.addAction('Fill blank', self.on_fill_blank)

        self.allow_overlap_action = self.toolbar.addAction('Allow overlap')
        self.allow_overlap_action.setToolTip('Hold Shift when using shortcut keys to temporarily switch modes')
        self.allow_overlap_action.setCheckable(True)
        self.allow_overlap_action.setChecked(not self.params['exclusive_mode'])
        self.allow_overlap_action.toggled.connect(lambda checked: self.params.param('exclusive_mode').setValue(not checked))


    def make_param_controller(self):
        self.params_controller = EpochEncoder_ParamController(parent=self, viewer=self)
        self.params_controller.setWindowFlags(QT.Qt.Window)


    def closeEvent(self, event):

        if self.changes_since_save != 0:
            text = 'Do you want to save epoch encoder changes before closing?'
            title = 'Save?'
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
        self.region.setRegion((self.spin_limit1.value(), self.spin_limit2.value()))
        self.plot.addItem(self.region, ignoreBounds=True)
        self.region.sigRegionChanged.connect(self.on_region_changed)

        self.vline = pg.InfiniteLine(angle=90, movable=False, pen=self.params['vline_color'])
        self.vline.setZValue(1) # ensure vline is above plot elements
        self.plot.addItem(self.vline)

        self.rect_items = []

        self.label_items = []
        for i, label in enumerate(self.source.possible_labels):
            color = self.by_label_params['label'+str(i), 'color']
            label_item = pg.TextItem(label, color=color, anchor=(0, 0.5), border=None, fill=self.params['label_fill_color'])
            label_item.setZValue(11)
            font = label_item.textItem.font()
            font.setPointSize(self.params['label_size'])
            label_item.setFont(font)
            self.plot.addItem(label_item)
            self.label_items.append(label_item)

        self.viewBox.xsize_zoom.connect(self.params_controller.apply_xsize_zoom)


    def on_controls_visibility_changed(self):
        if self.controls.isVisible():
            self.controls.hide()
            self.toggle_controls_visibility_action.setText('Show controls')
            self.toggle_controls_visibility_button.setArrowType(QT.RightArrow)
        else:
            self.controls.show()
            self.toggle_controls_visibility_action.setText('Hide controls')
            self.toggle_controls_visibility_button.setArrowType(QT.UpArrow)

    def show_params_controller(self):
        self.params_controller.show()

    def on_param_change(self):
        self.allow_overlap_action.setChecked(not self.params['exclusive_mode'])
        self.vline.setPen(color=self.params['vline_color'])
        for label_item in self.label_items:
            font = label_item.textItem.font()
            font.setPointSize(self.params['label_size'])
            label_item.setFont(font)
        self.refresh()

        if self.params['undo_history_size'] != self.history.maxlen:
            while len(self.history) > self.params['undo_history_size']:
                if self.history_position > 0:
                    # preferentially remove old states
                    self.history.popleft()
                    self.history_position -= 1
                else:
                    # otherwise remove newer, undone states
                    self.history.pop()
            self.history = deque(self.history, maxlen=self.params['undo_history_size'])

            # if the saved state was bumped off either end of the history
            # queue, it will no longer be reachable via undo/redo, so set
            # changes_since_save to None
            if self.changes_since_save is not None:
                if not (0 <= self.history_position - self.changes_since_save < len(self.history)):
                    self.changes_since_save = None

            self.refresh_toolbar()

    def assign_label_shortcuts(self, label, key):

        if label not in self.label_shortcuts:
            # create new shortcuts
            shortcut_without_modifier = QT.QShortcut(self)
            shortcut_with_modifier    = QT.QShortcut(self)
            shortcut_without_modifier.activated.connect(lambda: self.on_label_shortcut(label, False))
            shortcut_with_modifier   .activated.connect(lambda: self.on_label_shortcut(label, True))
            self.label_shortcuts[label] = (shortcut_without_modifier, shortcut_with_modifier)
        else:
            # get existing shortcuts
            shortcut_without_modifier, shortcut_with_modifier = self.label_shortcuts[label]

        # set/change the shortcut keys
        shortcut_without_modifier.setKey(QT.QKeySequence(key))
        shortcut_with_modifier   .setKey(QT.QKeySequence('Shift+' + key))

    def on_change_keys(self, refresh=True):

        for i, label in enumerate(self.source.possible_labels):
            # get string for shortcut key
            key = self.by_label_params['label'+str(i), 'key']

            # assign shortcuts without and with modifier key
            self.assign_label_shortcuts(label, key)

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
        xratio = self.params['xratio']
        t_start, t_stop = self.t-xsize*xratio , self.t+xsize*(1-xratio)
        self.request_data.emit(t_start, t_stop, [0])

    def on_data_ready(self, t_start, t_stop, visibles, data):
        #~ print('on_data_ready', self, t_start, t_stop, visibles, data)
        #~ self.plot.clear()

        for rect_item in self.rect_items:
            self.plot.removeItem(rect_item)
        self.rect_items = []

        self.graphicsview.setBackground(self.params['background_color'])

        times, durations, labels, ids = data[0]
        #~ print(data)
        n = len(self.source.possible_labels)

        for i, label in enumerate(labels):
            ind = self.source.possible_labels.index(label)
            color = self.by_label_params['label'+str(ind), 'color']
            color2 = QT.QColor(color)
            color2.setAlpha(130)
            if self.params['view_mode']=='stacked':
                ypos = n-ind-1
            else:
                ypos = 0
            item = RectItem([times[i], ypos, durations[i], .9], border=color, fill=color2, id=ids[i])
            item.clicked.connect(self.on_rect_clicked)
            item.doubleclicked.connect(self.on_rect_doubleclicked)
            item.setPos(times[i],  ypos)
            self.plot.addItem(item)
            self.rect_items.append(item)


        ticks = []
        for i, label_item in enumerate(self.label_items):
            if self.params['view_mode']=='stacked':
                color = self.by_label_params['label'+str(i), 'color']
                #~ label_item = pg.TextItem(label, color=color, anchor=(0, 0.5), border=None, fill=pg.mkColor((128,128,128, 120)))
                label_item.setColor(color)
                label_item.fill = pg.mkBrush(self.params['label_fill_color'])
                ypos = n-i-0.55
                label_item.setPos(t_start, ypos)
                ticks.append((ypos, self.by_label_params['label'+str(i), 'key']))
                label_item.show()
                #~ self.plot.addItem(label_item)
            else:
                label_item.hide()

        if self.params['keys_as_ticks'] and self.params['view_mode']=='stacked':
            self.plot.getAxis('left').setTicks([ticks, []])
        else:
            self.plot.getAxis('left').setTicks([])

        if self.range_group_box.isChecked():
            self.region.show()
        else:
            self.region.hide()

        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop, padding = 0.0)
        if self.params['view_mode']=='stacked':
            self.plot.setYRange( 0, n)
        else:
            self.plot.setYRange( 0, 1)

    def on_label_shortcut(self, label, modifier_used):

        range_selection_is_enabled = self.range_group_box.isChecked()

        if range_selection_is_enabled:
            # use selection for start and end of new epoch
            t_start = self.spin_limit1.value()
            t_stop = self.spin_limit2.value()
            duration = t_stop - t_start
        else:
            # use current time and step size to get end of new epoch
            duration = self.params['new_epoch_step']
            t_start = self.t
            t_stop = self.t + duration

        # delete existing epochs in the region where the new epoch will be inserted
        if (self.params['exclusive_mode'] and not modifier_used) or (not self.params['exclusive_mode'] and modifier_used):
            self.source.delete_in_between(t_start, t_stop)

        # create the new epoch
        self.source.add_epoch(t_start, duration, label)

        if not range_selection_is_enabled:
            # advance time by a step
            self.t += duration
            self.time_changed.emit(self.t)

        self.append_history()
        self.refresh()
        self.refresh_table()

    def on_merge_neighbors(self):
        self.source.merge_neighbors()
        self.append_history()
        self.refresh()
        self.refresh_table()

    def on_fill_blank(self):
        params = [{'name': 'method', 'type': 'list', 'value':'from_left', 'values' : ['from_left', 'from_right', 'from_nearest']}]
        dia = tools.ParamDialog(params, title='Fill blank method', parent=self)
        dia.resize(300, 100)
        if dia.exec_():
            d = dia.get()
            method = d['method']
            self.source.fill_blank(method=method)
            self.append_history()
            self.refresh()
            self.refresh_table()


    def on_save(self):
        self.source.save()
        self.changes_since_save = 0
        self.save_action.setEnabled(False)

    def append_history(self):
        # before appending a new state after the current position in the
        # history, remove any states that were undone
        while self.history_position < len(self.history) - 1:
            self.history.pop()

        if self.changes_since_save is not None:
            if self.changes_since_save < 0:
                # undone saved state was removed from history and so is
                # unreachable
                self.changes_since_save = None
            else:
                # saved state will be one more step in the past
                self.changes_since_save += 1

        self.history.append(deepcopy(self.source.all))
        self.history_position = len(self.history) - 1
        self.refresh_toolbar()

    def on_undo(self):
        if self.history_position > 0:
            self.history_position -= 1
            if self.changes_since_save is not None:
                self.changes_since_save -= 1
            self.source.all = deepcopy(self.history[self.history_position])
            self.refresh()
            self.refresh_table()
            self.refresh_toolbar()

    def on_redo(self):
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            if self.changes_since_save is not None:
                self.changes_since_save += 1
            self.source.all = deepcopy(self.history[self.history_position])
            self.refresh()
            self.refresh_table()
            self.refresh_toolbar()

    def refresh_toolbar(self):
        self.save_action.setEnabled(self.changes_since_save != 0)
        self.undo_action.setEnabled(self.history_position > 0)
        self.redo_action.setEnabled(self.history_position < len(self.history) - 1)

    def on_spin_limit_changed(self, v):
        # update region
        self.region.blockSignals(True)
        rgn = (self.spin_limit1.value(), self.spin_limit2.value())
        rgn = self.region.setRegion(rgn)
        self.region.blockSignals(False)

        # adjust spin box limits
        self.spin_limit1.setMaximum(self.spin_limit2.value())
        self.spin_limit2.setMinimum(self.spin_limit1.value())

    def on_region_changed(self):
        # update spin boxes
        self.spin_limit1.blockSignals(True)
        self.spin_limit2.blockSignals(True)
        rgn = self.region.getRegion()
        self.spin_limit1.setValue(rgn[0])
        self.spin_limit2.setValue(rgn[1])
        self.spin_limit1.blockSignals(False)
        self.spin_limit2.blockSignals(False)

        # adjust spin box limits
        self.spin_limit1.setMaximum(self.spin_limit2.value())
        self.spin_limit2.setMinimum(self.spin_limit1.value())

    def apply_region(self):

        rgn = self.region.getRegion()
        t = rgn[0]
        duration = rgn[1] - rgn[0]
        label = str(self.combo_labels.currentText())

        # delete existing epochs in the region where the new epoch will be inserted
        if self.params['exclusive_mode']:
            self.source.delete_in_between(rgn[0], rgn[1])

        # create the new epoch
        self.source.add_epoch(t, duration, label)

        self.append_history()
        self.refresh()
        self.refresh_table()

    def delete_region(self):

        rgn = self.region.getRegion()

        self.source.delete_in_between(rgn[0], rgn[1])

        self.append_history()
        self.refresh()
        self.refresh_table()

    def range_group_toggle(self):
        self.range_group_box.setChecked(not self.range_group_box.isChecked())
        self.on_range_visibility_changed()

    def on_range_visibility_changed(self, flag=None, refresh=True, shift_region=True):
        enabled = self.range_group_box.isChecked()

        for w in (self.spin_limit1, self.spin_limit2, self.combo_labels, self.but_apply_region, self.but_del_region):
            w.setEnabled(enabled)
        if enabled and shift_region:
            rgn = self.region.getRegion()
            rgn = (self.t, self.t + rgn[1] - rgn[0])
            self.region.setRegion(rgn)
        self.refresh()

    def set_limit1(self):
        if self.t<self.spin_limit2.value():
            self.spin_limit1.setValue(self.t)
            self.spin_limit1.repaint()  # needed on macOS

    def set_limit2(self):
        if self.t>self.spin_limit1.value():
            self.spin_limit2.setValue(self.t)
            self.spin_limit2.repaint()  # needed on macOS

    def refresh_table(self):
        self.table_widget.blockSignals(True)

        self.table_widget.clear()
        times, durations, labels = self.source.ep_times, self.source.ep_durations, self.source.ep_labels
        self.table_widget.setColumnCount(8)
        self.table_widget.setRowCount(times.size)
        self.table_widget.setHorizontalHeaderLabels(['', 'Start', 'Stop', 'Duration', 'Label', '', '', ''])

        # lock column widths for buttons to fixed button width
        self.table_widget.horizontalHeader().setMinimumSectionSize(self.table_button_fixed_width)
        for col in [SEEK_COL, SPLIT_COL, DUPLICATE_COL, DELETE_COL]:
            self.table_widget.horizontalHeader().setSectionResizeMode(col, QT.QHeaderView.Fixed)
            self.table_widget.setColumnWidth(col, self.table_button_fixed_width)

        for r in range(times.size):

            # seek button
            item = QT.QTableWidgetItem(self.table_widget_icons['seek'], '')
            item.setToolTip('Jump to epoch')
            self.table_widget.setItem(r, SEEK_COL, item)

            # start
            value = np.round(times[r], 6) # round to nearest microsecond
            item = QT.QTableWidgetItem('{}'.format(value))
            self.table_widget.setItem(r, START_COL, item)

            # stop
            value = np.round(times[r]+durations[r], 6) # round to nearest microsecond
            item = QT.QTableWidgetItem('{}'.format(value))
            self.table_widget.setItem(r, STOP_COL, item)

            # duration
            value = np.round(durations[r], 6) # round to nearest microsecond
            item = QT.QTableWidgetItem('{}'.format(value))
            self.table_widget.setItem(r, DURATION_COL, item)

            # label
            item = QT.QTableWidgetItem(labels[r])
            self.table_widget.setItem(r, LABEL_COL, item)

            # split button
            item = QT.QTableWidgetItem(self.table_widget_icons['split'], '')
            item.setToolTip('Split epoch at current time')
            self.table_widget.setItem(r, SPLIT_COL, item)

            # duplicate button
            item = QT.QTableWidgetItem(self.table_widget_icons['duplicate'], '')
            item.setToolTip('Duplicate epoch')
            self.table_widget.setItem(r, DUPLICATE_COL, item)

            # delete button
            item = QT.QTableWidgetItem(self.table_widget_icons['delete'], '')
            item.setToolTip('Delete epoch')
            self.table_widget.setItem(r, DELETE_COL, item)

        self.table_widget.blockSignals(False)

    def on_rect_clicked(self, id):

        # get index corresponding to epoch id
        ind = self.source.id_to_ind[id]

        # select the epoch in the data table
        self.table_widget.blockSignals(True)
        self.table_widget.setCurrentCell(ind, LABEL_COL) # select the label combo box
        self.table_widget.blockSignals(False)

    def on_rect_doubleclicked(self, id):

        # get index corresponding to epoch id
        ind = self.source.id_to_ind[id]

        # set region to epoch start and stop
        self.region.setRegion((self.source.ep_times[ind], self.source.ep_stops[ind]))

        # show the region if it isn't already visible
        self.range_group_box.setChecked(True)
        self.on_range_visibility_changed(shift_region=False)

    def on_seek_table(self, ind=None):
        if self.table_widget.rowCount()==0:
            return
        if ind is None:
            selected_ind = self.table_widget.selectedIndexes()
            if len(selected_ind)==0:
                return
            ind = selected_ind[0].row()
        self.t = self.source.ep_times[ind]
        self.refresh()
        self.time_changed.emit(self.t)

    def on_table_cell_click(self, row, col):
        if col == SEEK_COL:
            self.on_seek_table(row)
        elif col == SPLIT_COL:
            self.split_selected_epoch(row)
        elif col == DUPLICATE_COL:
            self.duplicate_selected_epoch(row)
        elif col == DELETE_COL:
            self.delete_selected_epoch(row)
        elif col == LABEL_COL:
            # replace text cell with a combo box
            combo_labels = QT.QComboBox()
            combo_labels.addItems(self.source.possible_labels)
            combo_labels.setCurrentText(self.source.ep_labels[row])
            combo_labels.currentIndexChanged.connect(
                lambda label_index, row=row: self.on_change_label(row, self.source.possible_labels[label_index])
            )
            self.table_widget.setCellWidget(row, LABEL_COL, combo_labels)
        else:
            return

    def on_table_cell_change(self, row, col):
        line_edit = self.table_widget.cellWidget(row, col)
        if not isinstance(line_edit, QT.QLineEdit): return
        new_text = line_edit.text()

        try:
            # convert string to number
            new_number = float(new_text)

        except ValueError:
            # an invalid number may have been entered, so restore the old value
            if col == START_COL:
                old_number = self.source.ep_times[row]
            elif col == STOP_COL:
                old_number = self.source.ep_times[row] + self.source.ep_durations[row]
            elif col == DURATION_COL:
                old_number = self.source.ep_durations[row]
            else:
                print('unexpected column changed')
                return
            old_number = np.round(old_number, 6) # round to nearest microsecond
            self.table_widget.blockSignals(True)
            self.table_widget.item(row, col).setText(str(old_number))
            self.table_widget.blockSignals(False)

        else:
            self.table_widget.blockSignals(True)

            # round and copy rounded number to table
            new_number = np.round(new_number, 6) # round to nearest microsecond
            self.table_widget.item(row, col).setText(str(new_number))

            if col == START_COL:

                # get the epoch stop time
                stop_time = self.source.ep_times[row] + self.source.ep_durations[row]

                # change epoch start time
                self.source.ep_times[row] = new_number

                # change epoch duration to keep stop time unchanged
                self.source.ep_durations[row] = stop_time - self.source.ep_times[row]

                # update epoch duration in table
                duration_line_edit = self.table_widget.item(row, DURATION_COL)
                new_duration = np.round(self.source.ep_durations[row], 6) # round to nearest microsecond
                duration_line_edit.setText(str(new_duration))

            elif col == STOP_COL:

                # change epoch duration for corresponding stop time
                self.source.ep_durations[row] = new_number-self.source.ep_times[row]

                # update epoch duration in table
                duration_line_edit = self.table_widget.item(row, DURATION_COL)
                new_duration = np.round(self.source.ep_durations[row], 6) # round to nearest microsecond
                duration_line_edit.setText(str(new_duration))

            elif col == DURATION_COL:

                # change epoch duration
                self.source.ep_durations[row] = new_number

                # update epoch stop time in table
                stop_line_edit = self.table_widget.item(row, STOP_COL)
                new_stop_time = self.source.ep_times[row] + self.source.ep_durations[row]
                new_stop_time = np.round(new_stop_time, 6) # round to nearest microsecond
                stop_line_edit.setText(str(new_stop_time))

            else:
                print('unexpected column changed')

            self.table_widget.blockSignals(False)

            self.append_history()

            # update plot
            self.refresh()
            # refresh_table is not called to avoid deselecting table cell

    def on_change_label(self, ind, new_label):

        # change epoch label
        self.source.ep_labels[ind] = new_label

        self.append_history()

        # update plot
        self.refresh()
        # refresh_table is not called to avoid deselecting table cell

    def delete_selected_epoch(self, ind=None):
        if self.table_widget.rowCount()==0:
            return
        if ind is None:
            selected_ind = self.table_widget.selectedIndexes()
            if len(selected_ind)==0:
                return
            ind = selected_ind[0].row()
        self.source.delete_epoch(ind)
        self.append_history()
        self.refresh()
        self.refresh_table()

    def duplicate_selected_epoch(self, ind=None):
        if self.table_widget.rowCount()==0:
            return
        if ind is None:
            selected_ind = self.table_widget.selectedIndexes()
            if len(selected_ind)==0:
                return
            ind = selected_ind[0].row()
        self.source.add_epoch(self.source.ep_times[ind], self.source.ep_durations[ind], self.source.ep_labels[ind])
        self.append_history()
        self.refresh()
        self.refresh_table()

    def split_selected_epoch(self, ind=None):
        if self.table_widget.rowCount()==0:
            return
        if ind is None:
            selected_ind = self.table_widget.selectedIndexes()
            if len(selected_ind)==0:
                return
            ind = selected_ind[0].row()
        if self.t <= self.source.ep_times[ind] or self.source.ep_stops[ind] <= self.t:
            return
        self.source.split_epoch(ind, self.t)
        self.append_history()
        self.refresh()
        self.refresh_table()
