# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division, absolute_import)



class BaseDataSource:
    def __init__(self):
        pass
    
    @property
    def nb_segment(self):
        pass
    
    @property
    def nb_channel(self):
        pass

    def get_t_start(self, seg_num=0):
        pass

    def get_t_stop(self, seg_num=0):
        pass
