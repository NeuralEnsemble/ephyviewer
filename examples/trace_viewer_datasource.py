from ephyviewer import mkQApp, MainViewer, TraceViewer
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
# TraceViewer normally accept a AnalogSignalSource but
# TraceViewer.from_numpy is facitilty function to bypass that
view1 = TraceViewer(source=source)


#put this veiwer in the main window
win.add_view(view1)

#show main window and run Qapp
win.show()
app.exec_()
