
import ephyviewer
import numpy as np
import os


def test_spikeinterface_viewer(interactive=False):
    import spikeinterface as si
    from spikeinterface.core.testing_tools import generate_recording, generate_sorting


    recording = generate_recording()
    sig_source = ephyviewer.SpikeInterfaceRecordingSource(recording=recording)

    sorting = generate_sorting()
    spike_source = ephyviewer.SpikeInterfaceSortingSource(sorting=sorting)

    app = ephyviewer.mkQApp()
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)

    view = ephyviewer.TraceViewer(source=sig_source, name='signals')
    win.add_view(view)

    view = ephyviewer.SpikeTrainViewer(source=spike_source, name='spikes')
    win.add_view(view)


    if interactive:
        win.show()
        app.exec_()
    else:
        # close thread properly
        win.close()



if __name__=='__main__':
    test_spikeinterface_viewer(interactive=True)
