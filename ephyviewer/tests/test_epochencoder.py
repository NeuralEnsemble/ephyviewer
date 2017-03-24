import numpy as np
import ephyviewer
from  ephyviewer.datasource.epochs import WritableEpochSource


def test_EpochEncoder():
    possible_labels = ['AAA', 'BBB', 'CCC', 'DDD']
    
    ep_times = np.arange(0, 10., .5)
    ep_durations = np.ones(ep_times.shape) * .25
    ep_labels = np.random.choice(possible_labels, ep_times.size)
    epoch = { 'time':ep_times, 'duration':ep_durations, 'label':ep_labels, 'name': 'MyFactor' }
    
    source = WritableEpochSource(epoch=epoch, possible_labels=possible_labels)

    app = ephyviewer.mkQApp()
    view = ephyviewer.EpochEncoder(source=source, name='Epoch encoder')
    
    win = ephyviewer.MainViewer(show_step=False, show_global_xsize=True, debug=False)
    win.add_view(view)
    win.show()
    
    app.exec_()


def test_EpochEncoder_settings():
    possible_labels = ['AAA', 'BBB', 'CCC', 'DDD']
    
    ep_times = np.arange(0, 10., .5)
    ep_durations = np.ones(ep_times.shape) * .25
    ep_labels = np.random.choice(possible_labels, ep_times.size)
    epoch = { 'time':ep_times, 'duration':ep_durations, 'label':ep_labels, 'name': 'MyFactor' }
    
    source = WritableEpochSource(epoch=epoch, possible_labels=possible_labels)

    app = ephyviewer.mkQApp()
    view = ephyviewer.EpochEncoder(source=source, name='Epoch encoder')
    
    win = ephyviewer.MainViewer(show_step=True, show_global_xsize=True, debug=False, settings_name='epoch_encode_test1', )
    win.add_view(view)
    win.show()
    
    app.exec_()
    
if __name__=='__main__':
    #~ test_EpochEncoder()
    test_EpochEncoder_settings()
