import numpy as np
import ephyviewer
from  ephyviewer.tests.testing_tools import make_fake_signals, make_fake_signals_with_scatter


def test_traceviewer():
    source = make_fake_signals()

    
    app = ephyviewer.mkQApp()
    view = ephyviewer.TraceViewer(source=source, name='trace')
    #~ view.refresh()
    
    
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)
    win.add_view(view)
    win.show()
    
    app.exec_()


def test_traceviewer_with_scatter():
    source = make_fake_signals_with_scatter()
    
    #~ exit()
    
    app = ephyviewer.mkQApp()
    view = ephyviewer.TraceViewer(source=source, name='trace_with_scatter')
    #~ view.refresh()
    
    
    win = ephyviewer.MainViewer(debug=True, show_auto_scale=True)
    win.add_view(view)
    win.show()
    
    app.exec_()    
    

if __name__=='__main__':
    test_traceviewer()
    #~ test_traceviewer_with_scatter()
