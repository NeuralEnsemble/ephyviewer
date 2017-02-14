# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)

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
    def __init__(self,   params, title = '', parent = None):
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