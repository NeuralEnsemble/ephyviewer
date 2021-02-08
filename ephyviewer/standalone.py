# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

import gc
from collections import OrderedDict

from .myqt import QT, QT_MODE
import pyqtgraph as pg


from .mainviewer import MainViewer, compose_mainviewer_from_sources
#~ from .traceviewer import TraceViewer
#~ from .epochviewer import EpochViewer
#~ from .eventlist import EventList
#~ from .spiketrainviewer import SpikeTrainViewer
from.tools import get_dict_from_group_param


from .datasource import get_sources_from_neo_rawio

# browse neo.rawios and add some gui_params
from neo.rawio import rawiolist
rawio_gui_params = {}
rawio_gui_params['RawBinarySignal'] = [
        {'name': 'dtype', 'type': 'list', 'values':['int16', 'uint16', 'float32', 'float64']},
        {'name': 'nb_channel', 'type': 'int', 'value':1},
        {'name': 'sampling_rate', 'type': 'float', 'value':10000., 'step': 1000., 'suffix': 'Hz', 'siPrefix': True},
        {'name': 'bytesoffset', 'type': 'int', 'value':0},
    ]

all_neo_rawio_dict = OrderedDict()
for rawio_class in rawiolist:
    name = rawio_class.__name__.replace('RawIO', '')
    #~ print(name)
    rawio_class.name = name
    rawio_class.gui_params = rawio_gui_params.get(name, None)
    assert name not in all_neo_rawio_dict
    all_neo_rawio_dict[name] = rawio_class




class WindowManager():
    def __init__(self):

        self.windows = []

    def open_dialog(self):
        dia = RawNeoOpenDialog()
        if dia.exec_():
            self.load_dataset(**dia.final_params)

    def load_dataset(self, neo_rawio_class=None, file_or_dir_names=[], io_params={}):
        #~ assert len(file_or_dir_names)==1
        if len(file_or_dir_names)!=1:
            return

        kargs = dict()
        if neo_rawio_class.rawmode.endswith('-file'):
            kargs['filename'] = file_or_dir_names[0]
        elif neo_rawio_class.rawmode.endswith('-dir'):
            kargs['dirname'] = file_or_dir_names[0]
        kargs.update(io_params)

        neorawio = neo_rawio_class(**kargs)
        neorawio.parse_header()
        print(neorawio)

        # initialize a new main window and populate viewers
        navigation_params = {}
        win = MainViewer(debug=False, settings_name=None, **navigation_params)
        sources = get_sources_from_neo_rawio(neorawio)
        compose_mainviewer_from_sources(sources, mainviewer=win)

        # add menus
        file_menu = win.menuBar().addMenu(win.tr("File"))
        do_open = QT.QAction('&Open', win, shortcut = "Ctrl+O")
        do_open.triggered.connect(self.open_dialog)
        file_menu.addAction(do_open)

        # store a reference to the window to prevent it from going out of scope
        # immediately and being destroyed
        self.windows.append(win)

        # delete window on close so that memory and file resources are released
        win.setAttribute(QT.WA_DeleteOnClose, True)
        win.destroyed.connect(
            lambda *args, i=len(self.windows)-1: self.free_resources(i))

        win.show()

        #~ for i, sig_source in enumerate(sources['signal']):
            #~ view = TraceViewer(source=sig_source, name='signal {}'.format(i))
            #~ view.params['scale_mode'] = 'same_for_all'
            #~ view.params['display_labels'] = True
            #~ view.auto_scale()
            #~ if i==0:
                #~ self.add_view(view)
            #~ else:
                #~ self.add_view(view, tabify_with='signal {}'.format(i-1))


        #~ for i, spike_source in enumerate(sources['spike']):
            #~ view = SpikeTrainViewer(source=spike_source, name='spikes')
            #~ self.add_view(view)

        #~ for i, ep_source in enumerate(sources['epoch']):
            #~ view = EpochViewer(source=ep_source, name='epochs')
            #~ self.add_view(view)

            #~ view = EventList(source=ep_source, name='Event list')
            #~ self.add_view(view, location='bottom',  orientation='horizontal')

    def free_resources(self, i):
        """
        Run garbage collection to unlock files and free memory for the closed
        window with index ``i``.
        Data files opened by Neo in lazy mode remain locked for as long as the
        RawIO objects pointing to them exist in memory. Normally such objects
        would be automatically garbage collected when they go out of scope,
        i.e., when the window that created them is closed. However, due to an
        issue in Neo, circular references to these objects are always created,
        so they persist even after the window is closed. This function performs
        a manual garbage collection after a window has been closed to clean up
        any lingering Neo objects that keep files locked. For more info about
        the issue, see https://github.com/NeuralEnsemble/python-neo/issues/684.
        """

        # first remove the last remaining reference to the closed window
        self.windows[i] = None

        # run garbage collection
        gc.collect()




class RawNeoOpenDialog(QT.QDialog):
    def __init__(self, parent=None):
        QT.QDialog.__init__(self, parent = parent)

        self.setWindowTitle('Open file or dir with neo.rawio')
        self.setModal(True)

        self.resize(600, 300)

        layout = QT.QVBoxLayout()
        self.setLayout(layout)


        #for step 'source_type'
        self.tree_params = pg.parametertree.ParameterTree(parent=self)
        self.tree_params.header().hide()
        layout.addWidget(self.tree_params)
        self.tree_params.hide()

        # for filenames
        self.but_addfiles = QT.QPushButton('Select file')
        layout.addWidget(self.but_addfiles)
        self.but_addfiles.clicked.connect(self.on_addfiles)
        self.but_addfiles.hide()
        self.list_files = QT.QListWidget()
        layout.addWidget(self.list_files)
        self.list_files.hide()
        layout.addStretch()

        self.but_next = QT.QPushButton('Next >')
        layout.addWidget(self.but_next)
        self.but_next.clicked.connect(self.validate_step)

        self.steps = ['source_type', 'filenames', 'io_params', ]
        self.display_step(self.steps[0])

        self.final_params = {}

    def display_step(self, step):
        self.actual_step = step

        if step=='source_type':
            source_types = list(all_neo_rawio_dict.keys())
            params = [{'name': 'format', 'type': 'list', 'values':source_types},
                            ]
            self.step_params = pg.parametertree.Parameter.create(name='Select format', type='group', children = params)
            self.tree_params.setParameters(self.step_params, showTop=True)
            self.tree_params.show()

        elif step=='filenames':
            self.but_addfiles.show()
            self.list_files.show()

        elif step=='io_params':
            params = self.neo_rawio_class.gui_params
            self.step_params = pg.parametertree.Parameter.create(name='Set params', type='group', children=params)
            self.tree_params.setParameters(self.step_params, showTop=True)
            self.tree_params.show()


    def validate_step(self):
        #~ print('validate_step', self.actual_step)
        step = self.actual_step
        if step=='source_type':
            self.neo_rawio_class = all_neo_rawio_dict[self.step_params['format']]
            self.final_params['neo_rawio_class'] = self.neo_rawio_class
            self.tree_params.hide()
            self.display_step('filenames')

        elif step=='filenames':
            file_or_dir_names = [self.list_files.item(i).text() for i in range(self.list_files.count())]
            if len(file_or_dir_names)==0: return
            self.final_params['file_or_dir_names'] = file_or_dir_names
            self.but_addfiles.hide()
            self.list_files.hide()

            if self.neo_rawio_class.gui_params is None:
                self.final_params['io_params'] = {}
                self.accept()

            else:
                self.display_step('io_params')

        elif step=='io_params':
            self.final_params['io_params'] = get_dict_from_group_param(self.step_params)
            self.tree_params.hide()
            self.display_step('mk_chan_grp')
            self.accept()


    def on_addfiles(self):
        #~ print('on_addfiles')
        #~ print(self.neo_rawio_class)
        #~ print(self.neo_rawio_class.rawmode)

        if self.neo_rawio_class.rawmode.endswith('-file'):
            fd = QT.QFileDialog(fileMode=QT.QFileDialog.ExistingFiles, acceptMode=QT.QFileDialog.AcceptOpen)
            #Todo play with rawio.extentsions
            fd.setNameFilters(['All (*)'])
        elif self.neo_rawio_class.rawmode.endswith('-dir'):
            fd = QT.QFileDialog(fileMode=QT.QFileDialog.DirectoryOnly, acceptMode=QT.QFileDialog.AcceptOpen)
            #~ fd.setNameFilters(['All (*)'])

        fd.setViewMode(QT.QFileDialog.Detail)
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.list_files.addItems(filenames)
