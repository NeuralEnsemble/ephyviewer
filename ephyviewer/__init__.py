# -*- coding: utf-8 -*-
from .version import version as __version__

#common tools
from .myqt import *
from .icons import *
from .datasource import *
from .mainviewer import MainViewer, compose_mainviewer_from_sources
from .navigation import NavigationToolBar



#Viewers
from .traceviewer import TraceViewer
from .videoviewer import VideoViewer
from .eventlist import EventList
from .epochviewer import EpochViewer
from .timefreqviewer import TimeFreqViewer
from .dataframeview import DataFrameView
from .spiketrainviewer import SpikeTrainViewer


#Encoders
from .epochencoder import EpochEncoder
