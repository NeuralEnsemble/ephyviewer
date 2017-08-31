from ephyviewer import mkQApp, MainViewer, TraceViewer
from ephyviewer import AnalogSignalSourceWithScatter
import ephyviewer
import numpy as np

#you must first create a main Qt application (for event loop)
app = mkQApp()

#create 16 signals with 100000 at 10kHz
sigs = np.random.rand(100000,16)
sample_rate = 1000.
t_start = 0.


#create fake 16 signals with sinus
sample_rate = 1000.
t_start = 0.
times = np.arange(1000000)/sample_rate
signals = np.sin(times*2*np.pi*5)[:, None]
signals = np.tile(signals, (1, 16))

#detect some crossing zeros
s0 = signals[:-2, 0]
s1 = signals[1:-1,0]
s2 = signals[2:,0]
peaks0,  = np.nonzero((s0<s1) & (s2<s1))
peaks1,  = np.nonzero((s0>s1) & (s2>s1))

#create 2 familly scatters from theses 2 indexes
scatter_indexes = {0: peaks0, 1: peaks1}
#and asign them to some channels each
scatter_channels = {0: [0, 5, 8], 1: [0, 5, 10]}
source = AnalogSignalSourceWithScatter(signals, sample_rate, t_start, scatter_indexes, scatter_channels)


#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)

#create a viewer for signal with TraceViewer
#connected to the signal source
view1 = TraceViewer(source=source)

view1.params['scale_mode'] = 'same_for_all'
view1.auto_scale()

#put this veiwer in the main window
win.add_view(view1)

#show main window and run Qapp
win.show()
app.exec_()
