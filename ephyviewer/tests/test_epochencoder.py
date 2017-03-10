import numpy as np
import ephyviewer
from  ephyviewer.datasource.epochs import WritableEpochSource


def test_EpochEncoder():
    possible_labels = ['a', 'b', 'c', 'd']
    
    ep_times = np.arange(0, 10., .5)
    ep_durations = np.ones(ep_times.shape) * .1
    ep_labels = np.random.choice(possible_labels, ep_times.size)
    epoch = { 'time':ep_times, 'duration':ep_durations, 'label':ep_labels, 'name': 'MyFactor' }
    
    source = WritableEpochSource(epoch=epoch, possible_labels=possible_labels)

    
    
    app = ephyviewer.mkQApp()
    view = ephyviewer.EpochEncoder(source=source, name='Epoch encoder')
    
    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)
    win.show()
    
    app.exec_()
    
    
if __name__=='__main__':
    test_EpochEncoder()
