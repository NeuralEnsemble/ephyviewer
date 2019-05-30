# -*- coding: utf-8 -*-
#~ from __future__ import (unicode_literals, print_function, division, absolute_import)



class BaseDataSource:
    def __init__(self):
        pass

    @property
    def nb_channel(self):
        raise(NotImplementedError)

    def get_channel_name(self, chan=0):
        raise(NotImplementedError)

    @property
    def t_start(self):
        raise(NotImplementedError)

    @property
    def t_stop(self):
        raise(NotImplementedError)
