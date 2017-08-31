from ephyviewer import mkQApp, MainViewer, SpikeTrainViewer
from ephyviewer import InMemorySpikeSource

import numpy as np

#you must first create a main Qt application (for event loop)
app = mkQApp()

#create fake 20 fake units with random firing
#put them in a da ta source
all_spikes =[]
for c in range(20):
    spike_times = np.random.rand(1000)*100.
    spike_times = np.sort(spike_times)
    all_spikes.append({ 'time':spike_times, 'name':'Unit#{}'.format(c) })
source = InMemorySpikeSource(all_spikes=all_spikes)

#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)



view1 = SpikeTrainViewer(source=source)


#put this veiwer in the main window
win.add_view(view1)

#show main window and run Qapp
win.show()


app.exec_()
