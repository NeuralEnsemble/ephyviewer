import numpy as np
import ephyviewer
from  ephyviewer.datasource.epochs import WritableEpochSource


def test_EpochEncoder(interactive=False):
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

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


def test_EpochEncoder_settings(interactive=False):
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

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


def test_EpochEncoder_empty(interactive=False):
    possible_labels = ['AAA', 'BBB', 'CCC', 'DDD']

    source = WritableEpochSource(epoch=None, possible_labels=possible_labels)
    source._t_stop = 10 # set to positive value so navigation has a finite range

    app = ephyviewer.mkQApp()
    view = ephyviewer.EpochEncoder(source=source, name='Epoch encoder')

    win = ephyviewer.MainViewer(show_step=False, show_global_xsize=True, debug=False)
    win.add_view(view)

    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()


if __name__=='__main__':
    test_EpochEncoder(interactive=True)
    test_EpochEncoder_settings(interactive=True)
    test_EpochEncoder_empty(interactive=True)
