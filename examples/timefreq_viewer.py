from ephyviewer import mkQApp, MainViewer, TraceViewer, TimeFreqViewer
from ephyviewer import InMemoryAnalogSignalSource
import ephyviewer
import numpy as np



#you must first create a main Qt application (for event loop)
app = mkQApp()

#create fake 16 signals with 100000 at 10kHz
sigs = np.random.rand(100000,16)
sample_rate = 1000.
t_start = 0.

#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)

#Create a datasource for the viewer
# here we use InMemoryAnalogSignalSource but
# you can alose use your custum datasource by inheritance
source = InMemoryAnalogSignalSource(sigs, sample_rate, t_start)

#create a viewer for signal with TraceViewer
view1 = TraceViewer(source=source, name='trace')
view1.params['scale_mode'] = 'same_for_all'
view1.auto_scale()

#create a time freq viewer conencted to the same source
view2 = TimeFreqViewer(source=source, name='tfr')

view2.params['show_axis'] = False
view2.params['timefreq', 'deltafreq'] = 1
view2.by_channel_params['ch3', 'visible'] = True


#add them to mainwindow
win.add_view(view1)
win.add_view(view2)


#show main window and run Qapp
win.show()
app.exec_()
