from ephyviewer import mkQApp, MainViewer, TraceViewer, SpectrogramViewer
from ephyviewer import InMemoryAnalogSignalSource
import ephyviewer
import numpy as np



# you must first create a main Qt application (for event loop)
app = mkQApp()

# create a fake signals 1 channel at 10kHz
# this emulate a moving frequency
sample_rate = 10000.
duration = 10.
times = np.arange(0, duration, 1./sample_rate, dtype='float64')
sigs = np.random.rand(times.size,1)
t_start = 0.
instantaneous_freqs = np.linspace(500, 3000, times.size)
instantaneous_phase = np.cumsum(instantaneous_freqs / sample_rate)*2*np.pi
sigs[:, 0] += np.sin(instantaneous_phase)



#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)

#Create a  signal source for the viewer
source = InMemoryAnalogSignalSource(sigs, sample_rate, t_start)

#create a viewer for signal with TraceViewer
view1 = TraceViewer(source=source, name='trace')
view1.params['scale_mode'] = 'same_for_all'
view1.params['xsize'] = 5.
view1.auto_scale()


#create a SpectrogramViewer on the same source
view2 = SpectrogramViewer(source=source, name='spectrogram')

view2.params['xsize'] = 5.
view2.params['colormap'] = 'inferno'
view2.params['scalogram', 'binsize'] = .1
view2.params['scalogram', 'scale'] = 'dB'
view2.params['scalogram', 'scaling'] = 'spectrum'

#add them to mainwindow
win.add_view(view1)
win.add_view(view2)


#show main window and run Qapp
win.show()
app.exec()
