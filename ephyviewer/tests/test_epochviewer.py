import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_epoch_source


def test_epoch_viewer():
    source = make_fake_epoch_source()
    
    
    app = ephyviewer.mkQApp()
    view = ephyviewer.EpochViewer(source=source, name='epoch')
    
    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)
    win.show()
    
    app.exec_()
    
    
if __name__=='__main__':
    test_epoch_viewer()
