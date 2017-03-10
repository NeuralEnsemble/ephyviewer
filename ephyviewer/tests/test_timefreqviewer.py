import ephyviewer


from  ephyviewer.tests.testing_tools import make_fake_signals


def test_traceviewer():
    source = make_fake_signals()

    
    app = ephyviewer.mkQApp()
    view = ephyviewer.TimeFreqViewer(source=source, name='timefreq')
    #~ view.refresh()
    
    #~ for c in range(source.nb_channel):
        #~ view.by_channel_params['ch'+str(c), 'visible'] = True
    
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)
    win.add_view(view)
    win.show()
    
    app.exec_()
    
    
if __name__=='__main__':
    test_traceviewer()
