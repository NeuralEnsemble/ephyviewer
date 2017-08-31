import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_spiketrain_source


def test_spiketrain_viewer():
    source = make_fake_spiketrain_source()
    
    
    app = ephyviewer.mkQApp()
    view = ephyviewer.SpikeTrainViewer(source=source, name='spikes')
    
    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)
    win.show()
    
    app.exec_()
    
    
if __name__=='__main__':
    test_spiketrain_viewer()
