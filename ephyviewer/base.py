# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from .myqt import QT
import pyqtgraph as pg
import numpy as np

import matplotlib.cm
import matplotlib.colors


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

    def auto_scale(self):
        pass



class MyViewBox(pg.ViewBox):
    doubleclicked = QT.pyqtSignal()
    ygain_zoom = QT.pyqtSignal(float)
    xsize_zoom = QT.pyqtSignal(float)
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.disableAutoRange()
    def mouseClickEvent(self, ev):
        if ev.double():
            ev.accept()
            self.doubleclicked.emit()
        else:
            ev.ignore()
    def wheelEvent(self, ev, axis=None):
        if ev.modifiers() == QT.Qt.ControlModifier:
            z = 5. if ev.delta()>0 else 1/5.
        else:
            z = 1.1 if ev.delta()>0 else 1/1.1
        self.ygain_zoom.emit(z)
        ev.accept()
    def mouseDragEvent(self, ev, axis=None):
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

    def set_layout(self, useOpenGL=None):
        # layout
        self.mainlayout = QT.QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.viewBox = MyViewBox()

        self.graphicsview  = pg.GraphicsView(useOpenGL=useOpenGL)
        self.mainlayout.addWidget(self.graphicsview)

        self.plot = pg.PlotItem(viewBox=self.viewBox)
        self.plot.hideButtons()
        self.graphicsview.setCentralItem(self.plot)

    def make_param_controller(self):
        if self.with_user_dialog and self._ControllerClass:
            self.all_params.blockSignals(True)
            self.params_controller = self._ControllerClass(parent=self, viewer=self)
            self.params_controller.setWindowFlags(QT.Qt.Window)
            self.all_params.blockSignals(False)
        else:
            self.params_controller = None

    def show_params_controller(self):
        self.params_controller.show()

    def on_param_change(self):
        self.refresh()

    def set_xsize(self, xsize):
        #~ print(self.__class__.__name__, 'set_xsize', xsize)
        if 'xsize' in [p.name() for p in self.params.children()]:
            self.params['xsize'] = xsize

    def set_settings(self, value):
        actual_value = self.all_params.saveState()
        #~ print('same tree', same_param_tree(actual_value, value))
        if same_param_tree(actual_value, value):
            # this prevent restore something that is not same tree
            # as actual. Possible when new features.
            self.all_params.blockSignals(True)
            self.all_params.restoreState(value)
            self.all_params.blockSignals(False)
        else:
            print('Not possible to restore setiings')

    def get_settings(self):
        return self.all_params.saveState()


def same_param_tree(tree1, tree2):
    children1 = list(tree1['children'].keys())
    children2 = list(tree2['children'].keys())
    if len(children1) != len(children2):
        return False

    for k1, k2 in zip(children1, children2):
        if k1!=k2:
            return False

        if 'children' in tree1['children'][k1]:
            if not 'children' in tree2['children'][k2]:
                return False
            #~ print('*'*5)
            #~ print('Recursif', k1)
            if not same_param_tree(tree1['children'][k1], tree2['children'][k2]):
                return False

    return True


class Base_ParamController(QT.QWidget):

    xsize_zoomed = QT.pyqtSignal(float)

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

    def apply_xsize_zoom(self, xmove):
        MIN_XSIZE = 1e-6
        factor = xmove/100.
        factor = max(factor, -0.5)
        factor = min(factor, 1)
        newsize = self.viewer.params['xsize']*(factor+1.)
        self.viewer.params['xsize'] = max(newsize, MIN_XSIZE)
        self.xsize_zoomed.emit(self.viewer.params['xsize'])



class Base_MultiChannel_ParamController(Base_ParamController):
    channel_visibility_changed = QT.pyqtSignal()
    channel_color_changed = QT.pyqtSignal()

    def __init__(self, parent=None, viewer=None, with_visible=True, with_color=True):
        Base_ParamController.__init__(self, parent=parent, viewer=viewer)


        h = QT.QHBoxLayout()
        self.mainlayout.addLayout(h)

        self.v1 = QT.QVBoxLayout()
        h.addLayout(self.v1)
        self.tree_params = pg.parametertree.ParameterTree()
        self.tree_params.setParameters(self.viewer.params, showTop=True)
        self.tree_params.header().hide()
        self.v1.addWidget(self.tree_params)

        self.tree_by_channel_params = pg.parametertree.ParameterTree()
        self.tree_by_channel_params.header().hide()
        h.addWidget(self.tree_by_channel_params)
        self.tree_by_channel_params.setParameters(self.viewer.by_channel_params, showTop=True)
        v = QT.QVBoxLayout()
        h.addLayout(v)

        #~ but = QT.PushButton('default params')
        #~ v.addWidget(but)
        #~ but.clicked.connect(self.reset_to_default)

        if hasattr(self.viewer, 'auto_scale'):
            but = QT.PushButton('Auto scale')
            v.addWidget(but)
            but.clicked.connect(self.auto_scale_viewer)


        if with_visible:
            if self.source.nb_channel>1:
                v.addWidget(QT.QLabel('<b>Select channel...</b>'))
                names = [p.name() + ': '+p['name'] for p in self.viewer.by_channel_params]
                self.qlist = QT.QListWidget()
                v.addWidget(self.qlist, 2)
                self.qlist.addItems(names)
                self.qlist.setSelectionMode(QT.QAbstractItemView.ExtendedSelection)
                self.qlist.doubleClicked.connect(self.on_double_clicked)

                for i in range(len(names)):
                    self.qlist.item(i).setSelected(True)
                v.addWidget(QT.QLabel('<b>and apply...<\b>'))


            but = QT.QPushButton('set visble')
            v.addWidget(but)
            but.clicked.connect(self.on_set_visible)

            self.channel_visibility_changed.connect(self.on_channel_visibility_changed)

        if with_color:
            v.addWidget(QT.QLabel('<b>Set color<\b>'))
            h = QT.QHBoxLayout()
            but = QT.QPushButton('Progressive')
            but.clicked.connect(self.on_automatic_color)
            h.addWidget(but,4)
            self.combo_cmap = QT.QComboBox()
            self.combo_cmap.addItems(['Accent', 'Dark2','jet', 'prism', 'hsv', ])
            h.addWidget(self.combo_cmap,1)
            v.addLayout(h)

            self.channel_color_changed.connect(self.on_channel_color_changed)

    #~ def reset_to_default(self):
        #~ self.viewer.make_params()
        #~ self.tree_params.setParameters(self.viewer.params, showTop=True)
        #~ self.tree_by_channel_params.setParameters(self.viewer.by_channel_params, showTop=True)
        #~ ## self.viewer.on_param_change()
        #~ self.viewer.refresh()

    def auto_scale_viewer(self):
        self.viewer.auto_scale()

    @property
    def selected(self):
        selected = np.ones(self.viewer.source.nb_channel, dtype=bool)
        if self.viewer.source.nb_channel>1:
            selected[:] = False
            selected[[ind.row() for ind in self.qlist.selectedIndexes()]] = True
        return selected


    @property
    def visible_channels(self):
        visible = [self.viewer.by_channel_params['ch{}'.format(i), 'visible'] for i in range(self.source.nb_channel)]
        return np.array(visible, dtype='bool')

    def on_set_visible(self):
        # apply
        self.viewer.by_channel_params.blockSignals(True)

        visibles = self.selected
        for i,param in enumerate(self.viewer.by_channel_params.children()):
            param['visible'] = visibles[i]

        self.viewer.by_channel_params.blockSignals(False)
        self.channel_visibility_changed.emit()

    def on_double_clicked(self, index):
        self.viewer.by_channel_params.blockSignals(True)
        visibles = self.selected
        for i,param in enumerate(self.viewer.by_channel_params.children()):
            param['visible'] = (i==index.row())
        self.viewer.by_channel_params.blockSignals(False)
        self.channel_visibility_changed.emit()

    def on_automatic_color(self, cmap_name = None):
        cmap_name = str(self.combo_cmap.currentText())
        n = np.sum(self.selected)
        if n==0: return
        cmap = matplotlib.cm.get_cmap(cmap_name , n)

        self.viewer.by_channel_params.blockSignals(True)
        for i, c in enumerate(np.nonzero(self.selected)[0]):
            color = [ int(e*255) for e in  matplotlib.colors.ColorConverter().to_rgb(cmap(i)) ]
            self.viewer.by_channel_params['ch{}'.format(c), 'color'] = color
        self.viewer.all_params.sigTreeStateChanged.connect(self.viewer.on_param_change)
        self.viewer.by_channel_params.blockSignals(False)
        self.channel_color_changed.emit()

    def on_channel_visibility_changed(self):
        self.viewer.refresh()

    def on_channel_color_changed(self):
        self.viewer.refresh()
