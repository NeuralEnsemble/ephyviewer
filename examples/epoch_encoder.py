"""
ephyviewer also propose an epoch encoder.
which can be used with key short cuts to encode levels or with the mouse 
defining limits.

The main trick is that the source must subclasse because the write method
is not writen, so it let flexibility for the ouput format.

Here an example of epoch encode that same file with simple csv.

"""

import os
from ephyviewer import mkQApp, MainViewer, TraceViewer, WritableEpochSource, EpochEncoder
import numpy as np
import pandas as pd 


class CvsEpochSource(WritableEpochSource):
    def __init__(self, output_filename, possible_labels):
        self.output_filename = output_filename
        self.filename = output_filename
        
        
        if os.path.exists(self.filename):
            # if file already exists load previous epoch
            df = pd.read_csv(self.filename,  index_col=None, sep='\t')
            times = df['time'].values
            durations = df['duration'].values
            labels = df['label'].values

            # fix due to rounding errors with CSV for some epoch
            # time[i]+duration[i]>time[i+1]
            # which to lead errors in GUI
            # so make a patch here
            mask1 = (times[:-1]+durations[:-1])>times[1:]
            mask2 = (times[:-1]+durations[:-1])<(times[1:]+1e-9)
            mask = mask1 & mask2
            errors, = np.nonzero(mask)
            durations[errors] = times[errors+1] - times[errors]
            # end fix

            epoch = {'time': times,
                            'duration':durations,
                            'label':labels,
                            'name': 'animal_state'}
        else:
            # if file NOT exists take empty.
            s = max([len(l) for l in possible_labels])
            epoch = {'time': np.array([], dtype='float64'),
                            'duration':np.array([], dtype='float64'),
                            'label': np.array([], dtype='U'+str(s)),
                            'name': 'animal_state'}

        WritableEpochSource.__init__(self, epoch, possible_labels)

    def save(self):
        df = pd.DataFrame()
        df['time'] = self.all[0]['time']
        df['duration'] = self.all[0]['duration']
        df['label'] = self.all[0]['label']
        df.to_csv(self.filename, index=False, sep='\t')



# lets encode some dev mood along the day
possible_labels = ['euphoric', 'nervous', 'hungry',  'triumphant']

filename = 'example_dev_mood_encoder.csv'
source_epoch = CvsEpochSource(filename, possible_labels)



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















