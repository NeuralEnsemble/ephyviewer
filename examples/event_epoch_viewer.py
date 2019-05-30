from ephyviewer import mkQApp, MainViewer, EpochViewer,EventList
from ephyviewer import InMemoryEventSource, InMemoryEpochSource
import ephyviewer
import numpy as np



#Create one data source with 3 event channel
all_events = []
for c in range(3):
    ev_times = np.arange(0, 10., .5) + c*3
    ev_labels = np.array(['Event{} num {}'.format(c, i) for i in range(ev_times.size)], dtype='U')
    all_events.append({ 'time':ev_times, 'label':ev_labels, 'name':'Event{}'.format(c) })
source_ev = InMemoryEventSource(all_events=all_events)


#Create one data source with 2 epoch channel
all_epochs = []
for c in range(3):
    ep_times = np.arange(0, 10., .5) + c*3
    ep_durations = np.ones(ep_times.shape) * .1
    ep_labels = np.array(['Event{} num {}'.format(c, i) for i in range(ep_times.size)], dtype='U')
    all_epochs.append({ 'time':ep_times, 'duration':ep_durations, 'label':ep_labels, 'name':'Event{}'.format(c) })
source_ep = ephyviewer.InMemoryEpochSource(all_epochs=all_epochs)




#you must first create a main Qt application (for event loop)
app = mkQApp()


#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)


view1 = EpochViewer(source=source_ep, name='epoch')
view1.by_channel_params['ch0', 'color'] = '#AA00AA'
view1.params['xsize'] = 6.5

view2 = EventList(source=source_ev, name='event')


#add them to mainwindow
win.add_view(view1)
win.add_view(view2, location='bottom',  orientation='horizontal')


#show main window and run Qapp
win.show()
app.exec_()
