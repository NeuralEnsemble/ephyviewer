"""
ephyviewer also propose an epoch encoder.
which can be used with key short cuts to encode levels or with the mouse 
defining limits.

ephyviewer makes available a CsvEpochSource class, which inherits from
WritableEpochSource. If you would like to customize reading and writing epochs
to files, you can write your own subclass of WritableEpochSource that
implements the __init__() (for reading) and save() (for writing) methods.

Here is an example of an epoch encoder that uses CsvEpochSource.

"""

from ephyviewer import mkQApp, MainViewer, TraceViewer, CsvEpochSource, EpochEncoder
import numpy as np



# lets encode some dev mood along the day
possible_labels = ['euphoric', 'nervous', 'hungry',  'triumphant']

filename = 'example_dev_mood_encoder.csv'
source_epoch = CsvEpochSource(filename, possible_labels)



#you must first create a main Qt application (for event loop)
app = mkQApp()

#create fake 16 signals with 100000 at 10kHz
sigs = np.random.rand(100000,16)
sample_rate = 1000.
t_start = 0.

#Create the main window that can contain several viewers
win = MainViewer(debug=True, show_auto_scale=True)

#create a viewer for signal
view1 = TraceViewer.from_numpy(sigs, sample_rate, t_start, 'Signals')
win.add_view(view1)
view1.params['scale_mode'] = 'same_for_all'
view1.params['display_labels'] = True

#create a viewer for the encoder itselfd
view2 = EpochEncoder(source=source_epoch, name='Dev mood states along day')
win.add_view(view2)


#show main window and run Qapp
win.show()


app.exec_()


# press 'a', 'z', 'e', 'r' to encode state.
# or press 'sho/hide range' and 'apply'















