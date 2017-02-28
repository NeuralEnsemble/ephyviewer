import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_signals


def test_traceviewer():
    source = make_fake_signals()

    
    app = ephyviewer.mkQApp()
    view = ephyviewer.TimeFreqViewer(source=source, name='timefreq')
    #~ view.refresh()
    
    
    win = ephyviewer.MainViewer(debug=True)
    win.add_view(view)
    win.show()
    
    app.exec_()
    
    
if __name__=='__main__':
    test_traceviewer()
