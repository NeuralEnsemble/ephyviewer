"""
Here is an example of opening viewers directly from neo objects.

There are two approaches:
   * create each viewer with class method (TraceViewer.from_neo_analogsignal, ...)
   * magically create all sources by providing the neo.Segment

"""
from ephyviewer import mkQApp, MainViewer, TraceViewer, SpikeTrainViewer, EpochViewer, EventList
from ephyviewer import get_sources_from_neo_segment, compose_mainviewer_from_sources
import numpy as np


from neo.test.generate_datasets import generate_one_simple_segment
import neo


# here we generate a segment with several objects
# (this is a bad example because it mimics old neo behavior for signals (one channel=one object))
neo_seg = generate_one_simple_segment(supported_objects=[neo.Segment, neo.AnalogSignal, neo.Event, neo.Epoch, neo.SpikeTrain])

# the global QT app
app = mkQApp()


##############################
# case 1 : create viewers one at a time directly from neo objects in memory
win = MainViewer(show_auto_scale=True)

# from one neo.AnalogSignal
view1 = TraceViewer.from_neo_analogsignal(neo_seg.analogsignals[0], 'sigs')
win.add_view(view1)

# from several neo.SpikeTrains (3 spiketrains here)
view2 = SpikeTrainViewer.from_neo_spiketrains(neo_seg.spiketrains[0:3], 'spikes')
win.add_view(view2)

# from several neo.Epoch
view3 = EpochViewer.from_neo_epochs(neo_seg.epochs, 'epochs')
win.add_view(view3)

# from several neo.Event
view4 = EventList.from_neo_events(neo_seg.events, 'events')
win.add_view(view4, location='bottom',  orientation='horizontal')

win.show()





##############################
# case 2 : automagically create data sources and a complete window from a neo segment
sources = get_sources_from_neo_segment(neo_seg)
win2 = compose_mainviewer_from_sources(sources)
win2.show()


app.exec_()
