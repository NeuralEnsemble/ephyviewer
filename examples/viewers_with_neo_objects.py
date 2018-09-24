"""
Here an example to open viewer directly from neo objects.

There are two approach:
   * create each viewer with class method (TraceViewer.from_ne_analogsignal, ...)
   * magically create all source by providing the neo.Segment


"""
from ephyviewer import mkQApp, MainViewer, TraceViewer, SpikeTrainViewer, EpochViewer
from ephyviewer import get_sources_from_neo_segment, compose_mainviewer_from_sources
import numpy as np


from neo.test.generate_datasets import generate_one_simple_segment
import neo


# here with generate a segment with several object
# (this is a bad example because it mimics old neo behavior for signals (one channel=one object))
neo_seg = generate_one_simple_segment(supported_objects=[neo.Segment, neo.AnalogSignal, neo.Epoch, neo.SpikeTrain])

# the global QT app
app = mkQApp()


##############################
# case1 : object by object
win = MainViewer(show_auto_scale=True)

# from one neo.AnalogSignal
view1 = TraceViewer.from_neo_analogsignal(neo_seg.analogsignals[0], 'sigs')
win.add_view(view1)

# from several neo.SpikeTrains (3 spiketrains here)
view2 = SpikeTrainViewer.from_neo_spiketrains(neo_seg.spiketrains[0:3], 'spikes')
win.add_view(view2)

# from several neo.SpikeTrains (3 spiketrains here)
view3 = EpochViewer.from_neo_epochs(neo_seg.epochs, 'epochs')
win.add_view(view3)

win.show()





##############################
# case 2 : automagic create window from automagic sources
sources = get_sources_from_neo_segment(neo_seg)
win2 = compose_mainviewer_from_sources(sources)
win2.show()


app.exec_()    