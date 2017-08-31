from ephyviewer import mkQApp, MainViewer, TraceViewer
import numpy as np

#you must first create a main Qt application (for event loop)
app = mkQApp()

#create fake 16 signals with 100000 at 10kHz
sigs = np.random.rand(100000,16)
sample_rate = 1000.
t_start = 0.

#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)

#create a viewer for signal with TraceViewer
# TraceViewer normally accept a AnalogSignalSource but
# TraceViewer.from_numpy is facitilty function to bypass that
view1 = TraceViewer.from_numpy(sigs, sample_rate, t_start, 'Signals')

#Parameters can be set in script
view1.params['scale_mode'] = 'same_for_all'
view1.params['display_labels'] = True

#And also parameters for each channel
view1.by_channel_params['ch0', 'visible'] = False
view1.by_channel_params['ch15', 'color'] = '#FF00AA'

#This is needed when scale_mode='same_for_all'
#to recompute the gain
#this avoid to push auto_scale button
view1.auto_scale()

#put this veiwer in the main window
win.add_view(view1)

#show main window and run Qapp
win.show()


app.exec_()
