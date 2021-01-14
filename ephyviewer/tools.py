# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)

from functools import lru_cache

from .myqt import QT
import pyqtgraph as pg


def get_dict_from_group_param(param, cascade = False):
    """
    Transform pyqtgraph params to dict.
    """
    assert param.type() == 'group'
    d = {}
    for p in param.children():
        if p.type() == 'group':
            if cascade:
                d[p.name()] = get_dict_from_group_param(p, cascade = True)
            continue
        else:
            d[p.name()] = p.value()
    return d

class ParamDialog(QT.QDialog):
    """
    Create a dialog with pyqtgraph params systrem.
    """
    def __init__(self,   params, title='', parent=None):
        QT.QDialog.__init__(self, parent = parent)

        self.setWindowTitle(title)
        self.setModal(True)

        self.params = pg.parametertree.Parameter.create( name=title, type='group', children = params)

        layout = QT.QVBoxLayout()
        self.setLayout(layout)

        self.tree_params = pg.parametertree.ParameterTree(parent  = self)
        self.tree_params.header().hide()
        self.tree_params.setParameters(self.params, showTop=True)
        #~ self.tree_params.setWindowFlags(QtCore.Qt.Window)
        layout.addWidget(self.tree_params)

        but = QT.QPushButton('OK')
        layout.addWidget(but)
        but.clicked.connect(self.accept)

    def get(self):
        return get_dict_from_group_param(self.params)




def create_plot_grid(graphiclayout, nb_column, visible_channels, ViewBoxClass=pg.ViewBox, vb_params={}):
    nb_channel = visible_channels.size
    nb_visible =sum(visible_channels)

    graphiclayout.clear()
    plots = [None] * nb_channel
    #~ images = [None] * nb_channel
    r,c = 0,0

    rowspan = nb_column
    colspan = nb_visible//nb_column
    graphiclayout.ci.currentRow = 0
    graphiclayout.ci.currentCol = 0
    for i in range(nb_channel):
        if not visible_channels[i]: continue

        viewBox = ViewBoxClass(**vb_params)
        #~ viewBox.setAspectLocked()
        plot = pg.PlotItem(viewBox=viewBox)
        plot.hideButtons()
        #~ plot.showAxis('left', False)
        #~ plot.showAxis('bottom', False)

        graphiclayout.addItem(plot, r, c)  # , rowspan, colspan)
        if r not in graphiclayout.ci.rows:
            graphiclayout.ci.rows[r] = {}
        graphiclayout.ci.rows[r][c] = plot
        graphiclayout.ci.items[plot] = [(r,c)]
        plots[i] = plot

        #~ images[i] = image = pg.ImageItem()
        #~ image.setPxMode(True)
        #~ plot.addItem(image)

        c+=1
        if c==nb_column:
            c=0
            r+=1

    return plots


@lru_cache(maxsize=None)
def mkCachedBrush(rgba):
    '''Create a QBrush from a color and cache it'''
    return pg.mkBrush(rgba)
